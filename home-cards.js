/* Real module navigation; only the home deck is managed here. */
(() => {
  const root = document.getElementById('home-page');
  const stage = root.querySelector('.card-stage');
  const cards = [...root.querySelectorAll('.module-card')];
  const modules = [
    {name:'四柱八字', intro:'从出生时空出发，看见自己的长期结构。', features:[['命盘研判','chart'],['岁运时间轴','timing'],['问一件事','question'],['合缘','affinity']]},
    {name:'塔罗占问', intro:'给此刻的具体问题，留一个重新思考的空间。', features:[['开始占问','tarot'],['回看牌阵','tarot-history']]},
    {name:'紫微斗数', intro:'理解十二宫的关联。排盘仍在校准中，解读供研习参考。', features:[['十二宫与解读','ziwei'],['出生档案','profile']]}
  ];
  let active=0, gesture=null, suppressUntil=0;
  function select(index, announce=true) {
    active=(index+3)%3;
    cards.forEach((card,i)=>{
      let slot=(i-active+3)%3; if(slot===2)slot=-1;
      card.style.setProperty('--slot',slot);
      card.classList.toggle('selected',i===active);
      card.setAttribute('aria-label',modules[i].name+(i===active?'，当前选中':'，点击切换'));
    });
    root.querySelectorAll('[data-select]').forEach(b=>b.setAttribute('aria-pressed',String(Number(b.dataset.select)===active)));
    root.querySelector('[data-current-number]').textContent=String(active+1).padStart(2,'0');
    root.querySelector('[data-current-name]').textContent=modules[active].name;
    root.querySelector('[data-current-intro]').textContent=modules[active].intro;
    root.querySelector('[data-current-features]').replaceChildren(...modules[active].features.map(([name,route])=>{
      const a=document.createElement('a');a.className='feature-chip';a.href='#/'+route;a.dataset.route=route;a.textContent=name+' ↗';return a;
    }));
    if(announce)root.querySelector('[data-announcement]').textContent='已选择'+modules[active].name;
  }
  root.addEventListener('click',e=>{
    if(Date.now()<suppressUntil && e.target.closest('.card-stage')){e.preventDefault();e.stopPropagation();return;}
    const tab=e.target.closest('[data-select]');if(tab)select(Number(tab.dataset.select));
    const step=e.target.closest('[data-step]');if(step)select(active+Number(step.dataset.step));
    const card=e.target.closest('.module-card');if(card&&!e.target.closest('[data-enter]'))select(Number(card.dataset.index));
    const scroll=e.target.closest('[data-home-scroll]');if(scroll)document.getElementById(scroll.dataset.homeScroll).scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'auto':'smooth',block:'start'});
  });
  stage.addEventListener('keydown',e=>{
    if(['ArrowLeft','ArrowRight'].includes(e.key)){e.preventDefault();select(active+(e.key==='ArrowRight'?1:-1));cards[active].focus({preventScroll:true});}
    if((e.key==='Enter'||e.key===' ')&&e.target.matches('.module-card')){e.preventDefault();select(Number(e.target.dataset.index));}
  });
  stage.addEventListener('pointerdown',e=>{
    if(e.button!==0)return;
    gesture={id:e.pointerId,x:e.clientX,y:e.clientY,drag:false};
  });
  stage.addEventListener('pointermove',e=>{
    if(!gesture||gesture.id!==e.pointerId)return;
    const dx=e.clientX-gesture.x,dy=e.clientY-gesture.y;
    if(!gesture.drag&&Math.abs(dx)>10&&Math.abs(dx)>Math.abs(dy)){gesture.drag=true;stage.setPointerCapture(e.pointerId);stage.classList.add('dragging');}
    if(gesture.drag)stage.style.setProperty('--drag',Math.max(-110,Math.min(110,dx*.35))+'px');
  });
  function finish(e,cancel=false){
    if(!gesture||gesture.id!==e.pointerId)return;
    if(gesture.drag){if(!cancel&&Math.abs(e.clientX-gesture.x)>45)select(active+(e.clientX<gesture.x?1:-1));suppressUntil=Date.now()+300;}
    stage.classList.remove('dragging');stage.style.setProperty('--drag','0px');
    if(stage.hasPointerCapture(e.pointerId))stage.releasePointerCapture(e.pointerId);gesture=null;
  }
  stage.addEventListener('pointerup',e=>finish(e));stage.addEventListener('pointercancel',e=>finish(e,true));
  select(0,false);
})();
