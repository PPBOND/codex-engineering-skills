// Checks the reusable visual template, not the evidence in an actual report.
const assert=require('node:assert/strict');
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {chromium}=require('playwright');
(async()=>{
  const browser=await chromium.launch({channel:'chrome',headless:true});
  try{
    const page=await browser.newPage();
    const errors=[];page.on('pageerror',e=>errors.push(e.message));
    const source=fs.readFileSync(path.join(__dirname,'../assets/report.html'),'utf8');
    // Synthetic copy exercises a concrete deliverable and visible validation limits.
    const work={
      '工作类型':'工具优化',
      '具体交付物名称与动作':'Python 日志自动排查工具优化（测试样例）',
      '输入或处理对象':'指定数据的日志',
      '具体工具或功能及其动作':'Python 自动检查',
      '可观察的输出或行为':'异常及日志行号',
      '已有问题或需求背景，不编造历史缺陷':'需要从多份日志中查找同一条数据，人工核对容易遗漏。',
      '针对哪个工具或功能改变了什么，输入如何变为输出':'工具按实例和数据 key 筛选日志，检查写入和读取过程，输出异常及对应日志行。',
      '谁能用它做什么，已证实的收益及代价':'开发人员可以直接查看相关记录，减少人工翻查；尚未测量节省的时间。',
      '完成哪些动作，测试验证了哪个对象，是否发布与剩余事项':'工具样例测试通过；数据库恢复行为仍需单独验证，代码尚未发布。',
    };
    const sample=source.replace(/\{\{([^}]+)\}\}/g,(_,name)=>work[name]??(name.includes('宽度')?'50':name.includes('数值')?'12.5':'测试说明：解释原有问题、实际改动和价值，并明确当前验证与交付边界。'));
    await page.setContent(sample);
    assert.equal(await page.locator('.work-visual:visible').count(),1);
    assert.equal(await page.locator('.risk-journey:visible').count(),1);
    assert.equal(await page.locator('.work-explanation dd:visible').count(),4);
    assert.deepEqual(await page.locator('a[href^="#"]').evaluateAll(links=>links.filter(a=>!document.getElementById(a.hash.slice(1))).map(a=>a.hash)),[]);
    await page.locator('a[href="#work-evidence-1"]').click();
    assert(await page.locator('#work-evidence-1').evaluate(d=>d.open));
    await page.locator('a[href="#risk-evidence-1"]').click();
    assert(await page.locator('#risk-evidence-1').evaluate(d=>d.open));
    const state=await page.locator('details').evaluateAll(ds=>ds.map(d=>d.open));
    await page.evaluate(()=>{window.dispatchEvent(new Event('beforeprint'));window.dispatchEvent(new Event('beforeprint'));});
    assert(await page.locator('details').evaluateAll(ds=>ds.every(d=>d.open)));
    await page.emulateMedia({media:'print'});
    assert.equal(await page.locator('.work-explanation dd:visible').count(),4);
    await page.evaluate(()=>window.dispatchEvent(new Event('afterprint')));
    assert.deepEqual(await page.locator('details').evaluateAll(ds=>ds.map(d=>d.open)),state);
    await page.emulateMedia({media:'screen'});
    await page.evaluate(()=>document.querySelectorAll('details').forEach(d=>d.open=false));
    const previews=fs.mkdtempSync(path.join(os.tmpdir(),'work-weak-report-check-'));
    for(const width of [320,390,768,1280]){
      await page.setViewportSize({width,height:900});
      assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),`overflow ${width}`);
      assert.equal(await page.locator('.work-explanation dd:visible').count(),4);
      assert(await page.locator('.work-visual').evaluate(el=>[el,...el.querySelectorAll('h3,.node,dd')].every(n=>n.scrollWidth<=n.clientWidth+1&&n.scrollHeight<=n.clientHeight+1)),`work copy clipped ${width}`);
      assert(await page.locator('.risk-node').evaluateAll(nodes=>{const r=nodes.map(n=>n.getBoundingClientRect());return innerWidth<=700?r[0].bottom<=r[1].top&&r[1].bottom<=r[2].top:r[0].right<=r[1].left&&r[1].right<=r[2].left;}),`risk order ${width}`);
      if(width===390||width===1280)await page.locator('#work').screenshot({path:path.join(previews,`${width}.png`)});
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({passed:true,visibleExplanations:4,widths:[320,390,768,1280],previews}));
  }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
