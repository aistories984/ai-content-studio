// Real local temporary speech in disposable projects. No provider/account/credit action.
const { chromium } = require('../.tools/browser/node_modules/playwright');
const { spawn } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const assert = require('node:assert/strict');

(async () => {
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), 'native-audio-smoke-'));
  const env = { ...process.env, DIRECTOR_DATA: directory, DIRECTOR_NO_SEED: '1' };
  let server, browser, log;
  async function python(script) {
    return new Promise((resolve, reject) => {
      const child = spawn('.venv/bin/python', ['-c', script], { env, stdio: ['ignore', 'pipe', 'pipe'] });
      let stdout='', stderr='';
      child.stdout.on('data',x=>stdout+=x); child.stderr.on('data',x=>stderr+=x);
      child.on('error', reject);
      child.on('exit',code=>code===0?resolve(JSON.parse(stdout)):reject(new Error(stderr)));
    });
  }
  try {
    const fixture = await python(`import io,json,os
from PIL import Image
from studio.store import Store
s=Store(os.environ['DIRECTOR_DATA'])
p=s.create_project({'title':'Native audio browser fixture','workflow_id':'comic-to-flow','production_brief':{'topic':'A robot plants a seed','audience':'Technical test audience','format':'short','target_seconds':8,'style':'Illustrated'}})['id']
scene=s.save_scene(p,{'title':'Eight-second test scene','duration':8})
other=s.save_scene(p,{'title':'Six-second test scene','duration':6})
out=io.BytesIO(); Image.new('RGB',(32,32),'green').save(out,format='PNG')
for stage,kind in [('premise','premise'),('comic','comic'),('script','script')]:
    files=[(f'{i}.png',out.getvalue()) for i in range(10)] if stage=='comic' else None
    r=s.add_version(p,{'title':stage,'kind':kind,'stage':stage,'content':'The robot plants a seed.','inputs':s.next_action(p)['inputs']},uploaded=files)
    s.review(r['version_id'],'approved')
print(json.dumps({'project_id':p,'scene_id':scene,'other_scene_id':other}))
`);
    const probe=require('node:net').createServer();
    await new Promise(resolve=>probe.listen(0,'127.0.0.1',resolve));
    const port=probe.address().port; await new Promise(resolve=>probe.close(resolve));
    const base=`http://127.0.0.1:${port}`;
    log=fs.openSync('.tools/audio-browser-server.log','w');
    server=spawn('.venv/bin/python',['-m','uvicorn','studio.app:app','--host','127.0.0.1','--port',String(port)],{env,stdio:['ignore',log,log]});
    let ready=false;
    for(let i=0;i<80;i++){
      if(server.exitCode!==null)throw new Error('Temporary audio server exited');
      try{if((await fetch(`${base}/api/session`)).ok){ready=true;break;}}catch{}
      await new Promise(resolve=>setTimeout(resolve,100));
    }
    assert(ready,'Temporary audio server did not start');
    const voicesResponse=await fetch(`${base}/api/audio-voices`);
    assert.equal(voicesResponse.status,200,'Native voice discovery endpoint must exist');
    const capability=await voicesResponse.json();
    assert(capability.available,'This native audio smoke requires an installed local speech engine');
    const voice=capability.voices.find(v=>v.id==='Albert') || capability.voices.find(v=>v.language.startsWith('en'));
    assert(voice,'An explicitly selected installed English voice is required for this test');
    browser=await chromium.launch({headless:true});
    const page=await browser.newPage({viewport:{width:1440,height:1000}});
    const errors=[];page.on('pageerror',e=>errors.push(e.message));page.setDefaultTimeout(5000);
    await page.goto(base);
    await page.getByRole('button',{name:'Scratch audio',exact:true}).click();
    const dialog=page.getByRole('dialog');
    await dialog.getByRole('heading',{name:'Generate temporary dialogue',exact:true}).waitFor();
    const voiceField=dialog.getByLabel('Scratch voice for NARRATOR',{exact:true});
    assert.equal(await voiceField.inputValue(),'','User must explicitly choose a voice');
    assert.equal(await dialog.getByLabel('Line 1',{exact:true}).inputValue(),'','Demo text must not become production dialogue');
    assert(await dialog.getByRole('button',{name:'Generate scratch audio',exact:true}).isDisabled());
    await dialog.getByRole('button',{name:'Edit full timing source',exact:true}).click();
    const blankSource=await dialog.getByLabel('Source JSON',{exact:true}).inputValue();
    await dialog.getByLabel('Source JSON',{exact:true}).fill('{"characters":null,"lines":[null]}');
    assert(await dialog.getByRole('button',{name:'Generate scratch audio',exact:true}).isDisabled());
    await dialog.getByLabel('Source JSON',{exact:true}).fill(blankSource);
    await voiceField.selectOption(voice.id);
    await dialog.getByLabel('Line 1',{exact:true}).fill('The robot plants a seed.');
    await dialog.getByLabel('Scene package',{exact:true}).selectOption(fixture.other_scene_id);
    assert.equal(JSON.parse(await dialog.getByLabel('Source JSON',{exact:true}).inputValue()).target_duration,8,'Changing scenes must preserve authored source');
    assert.equal(await dialog.getByLabel('Line 1',{exact:true}).inputValue(),'The robot plants a seed.');
    assert(await dialog.getByRole('button',{name:'Generate scratch audio',exact:true}).isDisabled(),'Mismatched scene timing must be blocked');
    await dialog.getByLabel('Scene package',{exact:true}).selectOption(fixture.scene_id);
    const source=JSON.parse(await dialog.getByLabel('Source JSON',{exact:true}).inputValue());
    assert.equal(source.target_duration,8);
    assert.equal(source.jobs.length,1);assert.equal(source.jobs[0].end,8);
    assert.equal(source.characters.NARRATOR.voice,voice.id);
    assert.equal(source.lines[0].text,'The robot plants a seed.');
    await page.screenshot({path:'.tools/audio-form-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Audio form mobile overflow');
    await page.screenshot({path:'.tools/audio-form-mobile.png',fullPage:true});
    await page.setViewportSize({width:1440,height:1000});
    const queued=page.waitForResponse(r=>r.request().method()==='POST' && r.url()===`${base}/api/projects/${fixture.project_id}/audio`);
    await dialog.getByRole('button',{name:'Generate scratch audio',exact:true}).click();
    const response=await queued;assert.equal(response.status(),200,await response.text());
    const jobId=(await response.json()).job_id;
    let project,job;
    for(let i=0;i<120;i++){
      project=await(await fetch(`${base}/api/projects/${fixture.project_id}`)).json();
      job=project.jobs.find(j=>j.id===jobId);
      if(job && !['queued','running'].includes(job.status))break;
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    assert.equal(job.status,'completed',JSON.stringify(job));
    const artifact=project.artifacts.find(a=>a.kind==='audio');
    assert(artifact,'Measured audio artifact must be registered');
    const v=artifact.latest;
    assert.equal(v.status,'in_review');assert.equal(v.metadata.temporary_audio,true);
    assert.equal(v.metadata.timing_passed,true);
    assert(v.metadata.timing.lines[0].duration>0,'Measured speech duration must be real');
    assert.equal(v.metadata.duration,8);
    assert(v.files.some(f=>f.name.endsWith('.srt')));
    assert(v.files.some(f=>f.name==='timing.json'));
    assert(!v.files.some(f=>f.name==='wan-plan.json'),'Flow audio must not promote a legacy Wan provider plan');
    assert.equal(project.stage_status.find(s=>s.id==='audio').complete,false,'Passing timing is not creative approval');
    const index=v.files.findIndex(f=>f.name==='mix.wav');
    const wav=await fetch(`${base}/api/media/${v.id}/${index}`);
    assert.equal(wav.status,200);assert((await wav.arrayBuffer()).byteLength>44);
    await page.reload();
    await page.getByText('Temporary dialogue',{exact:false}).first().waitFor();
    await page.screenshot({path:'.tools/audio-desktop.png',fullPage:true});
    await page.setViewportSize({width:390,height:844});
    assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Audio UI mobile overflow');
    await page.screenshot({path:'.tools/audio-mobile.png',fullPage:true});
    assert.deepEqual(errors,[]);
    console.log('PASS: explicit installed voice, blank/scene-sized source, real local speech/mix/stems/cues, waiting human review, reload, desktop/mobile.');
  } finally {
    if(browser)await browser.close();
    if(server && server.exitCode===null){server.kill('SIGTERM');await new Promise(resolve=>server.once('exit',resolve));}
    if(log!==undefined)fs.closeSync(log);
    fs.rmSync(directory,{recursive:true,force:true});
  }
})().catch(e=>{console.error(e);process.exitCode=1;});
