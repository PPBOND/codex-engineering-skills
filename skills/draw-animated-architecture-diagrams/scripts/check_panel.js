/* Execute in the loaded page's developer console. Returns to the overview. */
(() => {
  'use strict';
  const config=JSON.parse(document.getElementById('live-config').textContent);
  const previous=document.getElementById('previous-flow'),next=document.getElementById('next-flow');
  const graph=document.getElementById('graph'),details=document.getElementById('details');
  const assert=(ok,message)=>{if(!ok)throw new Error(message);};
  const inside=(p,n,margin=3)=>p.x>n.x+margin&&p.x<n.x+n.w-margin&&p.y>n.y+margin&&p.y<n.y+n.h-margin;
  const wireStats=[];

  // Separate routes must neither cross nor share a segment, including endpoints.
  function wiresTouch([a,b],[c,d]){
    const between=(x,u,v)=>x>=Math.min(u,v)&&x<=Math.max(u,v);
    const horizontal=a[1]===b[1],otherHorizontal=c[1]===d[1];
    if(horizontal!==otherHorizontal){
      const [h0,h1,v0,v1]=horizontal?[a,b,c,d]:[c,d,a,b];
      return between(v0[0],h0[0],h1[0])&&between(h0[1],v0[1],v1[1]);
    }
    const axis=horizontal?0:1,fixed=1-axis;
    return a[fixed]===c[fixed]&&Math.max(Math.min(a[axis],b[axis]),Math.min(c[axis],d[axis]))<=Math.min(Math.max(a[axis],b[axis]),Math.max(c[axis],d[axis]));
  }

  // An arrow must meet its declared nodes and avoid crossing unrelated cards.
  function checkEdges(page){
    const headings=[...graph.querySelectorAll('.group-label')].map(text=>{
      const b=text.getBBox();return {x:b.x,y:b.y,w:b.width,h:b.height};
    });
    page.edges.forEach((edge,index)=>{
      const path=document.getElementById('edge-'+index),length=path.getTotalLength();
      edge.points.slice(1).forEach((point,i)=>assert(point[0]===edge.points[i][0]||point[1]===edge.points[i][1],'Non-orthogonal wire: '+page.id+'/'+index));
      const from=page.nodes.find(n=>n.id===edge.from),to=page.nodes.find(n=>n.id===edge.to);
      assert(from&&to,'Unknown endpoint: '+page.id+'/'+index);
      for(const [point,node] of [[edge.points[0],from],[edge.points.at(-1),to]]){
        const [x,y]=point;
        assert(x>=node.x&&x<=node.x+node.w&&y>=node.y&&y<=node.y+node.h,'Endpoint outside node');
        assert(x===node.x||x===node.x+node.w||y===node.y||y===node.y+node.h,'Endpoint not on border');
      }
      for(let distance=6;distance<length-6;distance+=8){
        const point=path.getPointAtLength(distance);
        const hit=page.nodes.find(node=>inside(point,node));
        assert(!hit,'Arrow crosses node: '+page.id+'/'+index+' -> '+hit?.id);
        assert(!headings.some(heading=>inside(point,heading,0)),'Arrow crosses heading: '+page.id+'/'+index);
      }
      if(page.overview)return;
      assert(edge.step>=1&&edge.step<=page.steps.length,'Invalid step number');
      if(edge.badge)assert(!page.nodes.some(n=>inside({x:edge.label[0],y:edge.label[1]},n,-15)),'Badge on node: '+page.id+'/'+index);
    });
    page.edges.forEach((edge,i)=>page.edges.slice(i+1).forEach(other=>{
      const segments=edge.points.slice(1).map((b,k)=>[edge.points[k],b]);
      const otherSegments=other.points.slice(1).map((b,k)=>[other.points[k],b]);
      assert(!segments.some(a=>otherSegments.some(b=>wiresTouch(a,b))),'Crossing/overlap: '+page.id+'/'+edge.from+'→'+edge.to+' / '+other.from+'→'+other.to);
    }));
    const captions=[...graph.querySelectorAll('.edge-caption')].map(text=>{
      const b=text.getBBox();return {x:b.x-3,y:b.y-2,w:b.width+6,h:b.height+4};
    });
    for(const box of captions){
      assert(!page.nodes.some(n=>Math.max(box.x,n.x)<Math.min(box.x+box.w,n.x+n.w)&&Math.max(box.y,n.y)<Math.min(box.y+box.h,n.y+n.h)),'Caption touches node: '+page.id);
      for(const path of graph.querySelectorAll('.edge')){
        for(let distance=0;distance<path.getTotalLength();distance+=4)
          assert(!inside(path.getPointAtLength(distance),box,0),'Caption covers wire: '+page.id);
      }
    }
    wireStats.push({page:page.id,arrows:page.edges.length,maxBends:Math.max(...page.edges.map(e=>e.points.length-2))});
    const badges=[...graph.querySelectorAll('.edge-badge')].map(n=>Number(n.dataset.step));
    assert(badges.length===page.steps.length,'Wrong badge count');
    assert(new Set(badges).size===badges.length,'Repeated step number');
    page.steps.forEach((step,i)=>assert(badges.includes(i+1),'Step '+(i+1)+' has no arrow'));
  }

  function checkPage(page,index){
    assert(document.getElementById('page-title').textContent===page.title,'Wrong page');
    assert(graph.querySelectorAll('.node').length===page.nodes.length,'Unrelated or missing component');
    for(const node of page.nodes)
      assert(node.h<80||node.widget||node.fields?.length||node.lines.some(Boolean),'Empty card body: '+page.id+'/'+node.id);
    assert(previous.disabled===(index===0)&&next.disabled===(index===config.pages.length-1),'Boundary buttons');
    assert(details.hidden===Boolean(page.overview),'Overview/detail panel');
    assert(details.querySelectorAll('.step').length===page.steps.length,'Step count');
    for(const child of [...page.nodes,...page.groups].filter(item=>item.parent)){
      const parent=page.groups.find(group=>group.id===child.parent);
      assert(parent&&child.x>=parent.x&&child.y>=parent.y&&child.x+child.w<=parent.x+parent.w&&child.y+child.h<=parent.y+parent.h,'Ownership boundary: '+page.id+'/'+child.id);
    }
    checkEdges(page);
    const text=details.innerHTML,title=document.getElementById('flow-name').textContent;
    const times=Array.from({length:120},(_,i)=>24*i/120+.013*i).concat([3.999,4,24,48.001]);
    for(const time of times){
      window.seek(time);
      assert(details.innerHTML===text,'Steps changed with time');
      assert(document.getElementById('flow-name').textContent===title,'Automatic page change');
      const errors=window.__check();assert(errors.length===0,page.id+': '+errors.join(', '));
    }
    window.seek(3);const frame=graph.innerHTML;
    window.seek(3.2);assert(graph.innerHTML!==frame,'Packets stopped');
    window.seek(3);assert(graph.innerHTML===frame,'Replay differs');
  }
  assert(window.__ready,'Page not ready');
  assert(document.title===config.title&&document.getElementById('brand-title').textContent===config.title,'Wrong document branding');
  assert(document.getElementById('source-note').textContent===config.sourceNote,'Wrong source note');
  while(!previous.disabled)previous.click();
  config.pages.forEach((page,index)=>{checkPage(page,index);next.click();});
  for(let index=config.pages.length-2;index>=0;index--){
    previous.click();assert(document.getElementById('page-title').textContent===config.pages[index].title,'Previous page');
  }
  previous.click();assert(document.getElementById('page-title').textContent===config.pages[0].title,'First boundary');
  window.seek(0);
  return {result:'PASS: '+config.pages.length+' pages, '+config.pages.length*124+' frames; separate wires, unique numbers, endpoints, boundaries, fixed text, navigation and moving packets',wireStats};
})();
