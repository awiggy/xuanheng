(function () {
  const theme = window.PROTOTYPE_THEME || { key: "mist", name: "雾白观象", note: "留白与柔光" };
  const pages = [
    ["home", "入口首页", "统一入口与档案上下文"],
    ["chart-empty", "命盘 · 空状态", "未选择档案"],
    ["chart-report", "命盘 · 报告", "四柱与研判结果"],
    ["timing-empty", "岁运 · 空状态", "未选择档案"],
    ["timing", "岁运 · 详情", "大运、流年、流月"],
    ["question-empty", "问事 · 空状态", "保留完整工作台骨架"],
    ["question", "问事 · 使用态", "模式识别与问答"],
    ["profiles", "我的档案", "档案管理"],
    ["profile-edit", "编辑出生资料", "三历录入与真太阳时"],
    ["principles", "设计理念", "术语与产品原则"]
  ];
  const routeMap = new Map(pages.map((p, index) => [p[0], { id: p[0], title: p[1], note: p[2], index }]));
  let currentView = "home";
  let currentMode = "fortune";
  let expandedYears = false;
  let expandedMonths = false;

  const modeContent = {
    random: {
      label: "随缘",
      helper: "从命盘中随机挑出此刻值得留意的一件事",
      placeholder: "也可以写下最近反复想到的一件事……",
      suggestions: ["今天最值得留意什么？", "最近有什么被我忽略？", "给我一个行动提醒"]
    },
    fortune: {
      label: "看运",
      helper: "识别时间与运势意图，调用岁运依据作答",
      placeholder: "例如：今年哪几个月适合换工作？",
      suggestions: ["今年哪几个月适合换工作？", "这个月求职能成功吗？", "近期适合主动谈加薪吗？"]
    },
    listen: {
      label: "倾听",
      helper: "结合命盘结构，整理性格、情绪与关系模式",
      placeholder: "例如：为什么我总在关系里过度承担？",
      suggestions: ["我为什么容易想太多？", "我的关系模式是什么？", "我该怎样恢复精力？"]
    },
    matter: {
      label: "问事",
      helper: "识别具体事件，限定时间范围并给出可核验依据",
      placeholder: "例如：我正在找产品经理工作，这个月拿到合适 offer 的机会如何？",
      suggestions: ["这个决定适合现在推进吗？", "我和 TA 适合继续吗？", "最近换城市合适吗？"]
    }
  };

  const iconNames = {
    chart: "chart", timing: "timeline", question: "message", profiles: "folder", principles: "sparkle"
  };

  function icon(name, cls = "") {
    return `<svg class="icon ${cls}" aria-hidden="true"><use href="#i-${name}"></use></svg>`;
  }

  function sprite() {
    return `<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>
      <symbol id="i-arrow" viewBox="0 0 24 24"><path d="M5 12h14M13 6l6 6-6 6"/></symbol>
      <symbol id="i-chart" viewBox="0 0 24 24"><path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/></symbol>
      <symbol id="i-timeline" viewBox="0 0 24 24"><path d="M5 4v16M19 4v16M5 8h14M5 16h14"/><circle cx="9" cy="8" r="2"/><circle cx="15" cy="16" r="2"/></symbol>
      <symbol id="i-message" viewBox="0 0 24 24"><path d="M4 5h16v11H9l-5 4V5z"/></symbol>
      <symbol id="i-folder" viewBox="0 0 24 24"><path d="M3 6h7l2 2h9v11H3V6z"/></symbol>
      <symbol id="i-sparkle" viewBox="0 0 24 24"><path d="m12 3 1.4 4.6L18 9l-4.6 1.4L12 15l-1.4-4.6L6 9l4.6-1.4L12 3zM19 15l.7 2.3L22 18l-2.3.7L19 21l-.7-2.3L16 18l2.3-.7L19 15z"/></symbol>
      <symbol id="i-grid" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></symbol>
      <symbol id="i-x" viewBox="0 0 24 24"><path d="m6 6 12 12M18 6 6 18"/></symbol>
      <symbol id="i-user" viewBox="0 0 24 24"><circle cx="12" cy="8" r="4"/><path d="M4 21c.8-4.2 3.5-6 8-6s7.2 1.8 8 6"/></symbol>
      <symbol id="i-plus" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></symbol>
      <symbol id="i-check" viewBox="0 0 24 24"><path d="m5 12 4 4L19 6"/></symbol>
      <symbol id="i-edit" viewBox="0 0 24 24"><path d="m4 20 4.5-1 10-10-3.5-3.5-10 10L4 20zM13.5 7l3.5 3.5"/></symbol>
      <symbol id="i-search" viewBox="0 0 24 24"><circle cx="10" cy="10" r="6"/><path d="m15 15 6 6"/></symbol>
      <symbol id="i-map" viewBox="0 0 24 24"><path d="M12 22s7-6.2 7-13a7 7 0 1 0-14 0c0 6.8 7 13 7 13z"/><circle cx="12" cy="9" r="2.5"/></symbol>
      <symbol id="i-globe" viewBox="0 0 24 24"><circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3.3 3 14.7 0 18M12 3c-3 3.3-3 14.7 0 18"/></symbol>
      <symbol id="i-sun" viewBox="0 0 24 24"><circle cx="12" cy="12" r="4"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/></symbol>
      <symbol id="i-moon" viewBox="0 0 24 24"><path d="M20 15.3A8 8 0 0 1 8.7 4a8 8 0 1 0 11.3 11.3z"/></symbol>
      <symbol id="i-calendar" viewBox="0 0 24 24"><rect x="3" y="5" width="18" height="16"/><path d="M7 2v6M17 2v6M3 10h18"/></symbol>
      <symbol id="i-chevron" viewBox="0 0 24 24"><path d="m7 9 5 5 5-5"/></symbol>
      <symbol id="i-layers" viewBox="0 0 24 24"><path d="m12 3 9 5-9 5-9-5 9-5zM3 12l9 5 9-5M3 16l9 5 9-5"/></symbol>
    </defs></svg>`;
  }

  function header() {
    const section = currentView.startsWith("chart") ? "chart" : currentView.startsWith("timing") ? "timing" : currentView.startsWith("question") ? "question" : currentView === "profiles" || currentView === "profile-edit" ? "profiles" : currentView === "principles" ? "principles" : "";
    return `<header class="site-header">
      <button class="brand" data-view="home" aria-label="返回玄衡首页">
        <span class="brand-mark">玄</span><span><span class="brand-name">玄衡</span><span class="brand-sub">Xuan Heng · Bazi</span></span>
      </button>
      <nav class="main-nav" aria-label="主导航">
        ${navButton("chart", "命盘研判", section)}
        ${navButton("timing", "岁运时间轴", section)}
        ${navButton("question", "问一件事", section)}
        ${navButton("principles", "设计理念", section)}
      </nav>
      <div class="header-actions">
        <span class="status-chip"><span class="status-dot"></span>分析服务可用</span>
        <button class="btn small" data-view="profiles">${icon("folder", "sm")}<span class="archive-label">我的档案</span></button>
        <button class="btn small" data-action="drawer" aria-label="打开十页预览目录">${icon("grid", "sm")}<span class="archive-label">10页</span></button>
      </div>
    </header>`;
  }

  function navButton(id, label, section) {
    const target = id === "chart" ? "chart-report" : id === "timing" ? "timing" : id;
    return `<button class="nav-button ${section === id ? "active" : ""}" data-view="${target}">${label}</button>`;
  }

  function pageHero(eyebrow, title, lead, action = "") {
    return `<div class="page-hero"><div><div class="eyebrow">${eyebrow}</div><h1>${title}</h1><p class="lead">${lead}</p></div>${action}</div>`;
  }

  function homeView() {
    return `<main class="page">
      <section class="panel home-hero">
        <div class="home-hero-inner">
          <div class="eyebrow">玄衡 · 01</div>
          <h1 class="home-title" aria-label="玄衡">玄衡</h1>
          <p class="lead" style="margin-inline:auto">从一份可核验的四柱命盘开始，看清所处阶段，再回答此刻最重要的一个问题。</p>
          <div class="home-actions"><button class="btn primary" data-view="chart-report">查看舒克的命盘 ${icon("arrow", "sm")}</button><button class="btn" data-view="profile-edit">新建档案</button></div>
        </div>
      </section>
      <div class="context-bar">
        <div class="context-profile"><span class="avatar">舒</span><div><strong>当前档案 · 舒克</strong><div class="micro">2002年6月15日 11:30 · 女 · 眉山市</div></div></div>
        <button class="btn small" data-view="profiles">切换档案 ${icon("arrow", "sm")}</button>
      </div>
      <section class="grid-3 section-gap">
        ${feature("chart", "命盘研判", "四柱、十神、五行与结构依据集中在一份报告内。", "chart-report")}
        ${feature("timeline", "岁运时间轴", "以大运为环境，以流年与节气流月观察变化。", "timing")}
        ${feature("message", "问一件事", "先识别意图，再调用对应命盘与岁运依据。", "question")}
      </section>
    </main>`;
  }

  function feature(iconName, title, text, target) {
    return `<article class="feature-card"><span class="icon-box">${icon(iconName, "lg")}</span><h3>${title}</h3><p class="muted">${text}</p><button class="btn ghost small" data-view="${target}">进入 ${icon("arrow", "sm")}</button></article>`;
  }

  function emptyView(kind) {
    const isChart = kind === "chart";
    return `<main class="page">
      ${pageHero(isChart ? "Chart · 命盘研判" : "Timing · 岁运", isChart ? "命盘研判" : "岁运时间轴", isChart ? "四柱排盘与解释都从一份明确的出生资料开始。" : "大运、流年与流月都依赖已完成排盘的档案。")}
      <section class="panel empty-stage">
        <div><span class="empty-icon">${icon(isChart ? "chart" : "timeline", "lg")}</span><h2>请先选择一份档案</h2><p>${isChart ? "选择后会在同一位置呈现命盘报告，不改变页面结构与操作重心。" : "选择后会在同一位置呈现大运、流年与节气流月，不制造空态与使用态断层。"}</p><button class="btn primary" data-view="profiles">前往我的档案 ${icon("arrow", "sm")}</button></div>
      </section>
    </main>`;
  }

  function chartView() {
    const pillars = [
      ["年柱", "偏印", "壬", "午", "藏干 丁火、己土"],
      ["月柱", "食神", "丙", "午", "藏干 丁火、己土"],
      ["日柱", "日主", "甲", "寅", "藏干 甲木、丙火、戊土"],
      ["时柱", "正财", "己", "巳", "藏干 丙火、庚金、戊土"]
    ];
    return `<main class="page">
      <section class="panel panel-pad stack">
        <div class="report-head"><div><div class="eyebrow">Personal chart · 已核验</div><h1 class="report-title">舒克的命盘报告</h1><p class="lead">2002年6月15日 11:30 → 真太阳时 10:25 · 女 · 眉山市</p></div><button class="btn" data-view="profile-edit">${icon("edit", "sm")} 编辑出生资料</button></div>
        <div class="notice">${icon("check")}<div><strong>排盘依据已就绪</strong><div class="micro">北京时区；经度 103.779001°；真太阳时修正 -64.9 分钟；四柱与岁运来自同一排盘结果。</div></div></div>
        <div><div class="section-head"><div><h2>四柱命盘</h2><p class="muted">日柱作为命主核心，其余三柱展示与日主的十神关系。</p></div><span class="micro">真太阳时 · Python 定气排盘</span></div><div class="pillars">${pillars.map((p,i)=>`<article class="pillar ${i===2?"day":""}"><span class="pillar-label">${p[0]}</span><span class="pillar-role">${p[1]}</span><div class="pillar-glyph">${p[2]}<br>${p[3]}</div><span class="pillar-foot">${p[4]}</span></article>`).join("")}</div></div>
        <div class="grid-2">
          <section class="panel panel-pad soft"><div class="section-head"><div><h3>五行构成</h3><p class="micro">结构参考，不以百分比直接断吉凶</p></div></div>${[["木",19],["火",46],["土",23],["金",4],["水",8]].map(x=>`<div class="bar-row"><span>${x[0]}</span><span class="bar-track"><span class="bar-fill" style="width:${x[1]}%"></span></span><strong>${x[1]}%</strong></div>`).join("")}</section>
          <section class="panel panel-pad soft"><div class="section-head"><div><h3>排盘提要</h3><p class="micro">用于连接命盘、岁运和问事</p></div></div><div class="summary-grid"><div class="summary-item"><span>日主</span><strong>甲木</strong></div><div class="summary-item"><span>月令</span><strong>午火</strong></div><div class="summary-item"><span>大运方向</span><strong>逆排</strong></div><div class="summary-item"><span>起运</span><strong>3岁1个月</strong></div></div></section>
        </div>
      </section>
    </main>`;
  }

  function timingView() {
    const luck = [["丙午","0岁-3岁1月"],["乙巳","3-12岁"],["甲辰","13-22岁"],["癸卯","23-32岁"],["壬寅","33-42岁"],["辛丑","43-52岁"],["庚子","53-62岁"],["己亥","63-72岁"],["戊戌","73-82岁"]];
    const years = [[24,"丙午",2026],[25,"丁未",2027],[26,"戊申",2028],[27,"己酉",2029],[28,"庚戌",2030],[29,"辛亥",2031],[30,"壬子",2032],[31,"癸丑",2033],[32,"甲寅",2034]];
    const months = [["立春","庚寅","2.4—3.4"],["惊蛰","辛卯","3.5—4.4"],["清明","壬辰","4.5—5.4"],["立夏","癸巳","5.5—6.4"],["芒种","甲午","6.5—7.6"],["小暑","乙未","7.7—8.6"],["立秋","丙申","8.7—9.6"],["白露","丁酉","9.7—10.7"],["寒露","戊戌","10.8—11.6"],["立冬","己亥","11.7—12.6"],["大雪","庚子","12.7—1.4"],["小寒","辛丑","1.5—2.3"]];
    return `<main class="page">
      ${pageHero("Timing · 岁运", "岁运时间轴", "以大运为环境、流年为引动，并以节气划分十二个流月。", `<button class="btn" data-view="chart-report">当前档案 · 舒克 ${icon("arrow","sm")}</button>`)}
      <section class="panel panel-pad"><div class="section-head"><div><div class="eyebrow">Decade luck</div><h2>大运走势</h2></div><span class="micro">当前 · 癸卯大运</span></div><div class="luck-strip">${luck.map((x,i)=>`<button class="luck-card ${i===3?"active":""}" data-action="luck"><strong>${x[0]}</strong><small>${x[1]}</small></button>`).join("")}</div><div class="timeline-note"><strong>癸卯 · 23—32岁</strong><div class="muted">癸水正印透出，卯木为根。适合深造、系统学习与建立稳定方法；合作中应明确边界，避免过度承担。</div></div></section>
      <section class="panel panel-pad section-gap"><div class="section-head"><div><div class="eyebrow">Annual flow</div><h2>本大运流年走势</h2><p class="muted">默认展示当前起五年，展开后查看完整大运。</p></div><button class="btn" data-action="years">${expandedYears?"收起":"展开"} ${icon("chevron","sm")}</button></div><div class="year-strip">${years.map((x,i)=>`<button class="year-card ${i===0?"active":""} extra-year" ${!expandedYears&&i>4?"hidden":""} data-year="${x[2]}"><small>${x[0]}岁</small><strong>${x[1]}</strong><small>${x[2]}年</small></button>`).join("")}</div><div class="period-detail"><strong>2026 · 丙午 · 24岁</strong><div class="muted">流年与原局午火叠加，行动意愿增强；适合明确目标、分段推进，重要决定需保留复核窗口。</div></div></section>
      <section class="panel panel-pad section-gap"><div class="section-head"><div><div class="eyebrow">Monthly flow</div><h2>流月走势</h2><p class="muted">以节气交接日划分，不按公历自然月切割。</p></div><button class="btn" data-action="months">${expandedMonths?"收起":"展开"} ${icon("chevron","sm")}</button></div><div class="month-strip">${months.map((x,i)=>`<button class="month-card ${i===6?"active":""}" ${!expandedMonths&&i>5?"hidden":""} data-month="${i}"><small>${x[0]}</small><strong>${x[1]}</strong><small>${x[2]}</small></button>`).join("")}</div><div class="period-detail"><strong>流月依据</strong><div class="muted">例如丙申月从 8月7日开始，至 9月6日结束；9月7日进入丁酉月。</div></div></section>
    </main>`;
  }

  function questionView(empty) {
    const data = modeContent[currentMode];
    return `<main class="page question-page">
      <section class="question-identity">
        <span class="service-chip"><span class="status-dot"></span>${empty ? "选择档案后可开始研判" : "研判服务正常 · 当前档案已载入"}</span>
        <h1 class="profile-name">${empty ? "未选择档案" : "舒克"}</h1>
        <div class="question-divider">${icon("sparkle")}</div>
        <p class="lead">${empty ? "先确认要研判的命盘，再进入同一套问事流程。" : "慢慢来，玄衡会陪你把问题说清楚。"}</p>
        <div class="mode-switch" aria-label="问事模式">
          ${modeButton("random", "随缘", "sparkle", empty)}${modeButton("fortune", "看运", "timeline", empty)}${modeButton("listen", "倾听", "message", empty)}${modeButton("matter", "问事", "chart", empty)}
        </div>
      </section>
      <section class="panel question-console">
        <div class="console-top"><div><strong>${empty ? "选择档案后，问题会在这里继续" : data.label + " · " + data.helper}</strong><div class="micro">${empty ? "不会跳转到另一种页面结构" : "当前依据：命盘报告、癸卯大运、2026丙午流年"}</div></div>${empty ? `<button class="btn primary" data-view="profiles">选择档案 ${icon("arrow","sm")}</button>` : ""}</div>
        <div class="composer"><textarea id="question-input" ${empty?"disabled":""} placeholder="${empty?"选择档案后即可输入问题":data.placeholder}"></textarea><button class="btn primary" data-action="ask" ${empty?"disabled":""}>${icon("sparkle")}开始研判</button></div>
        <div class="console-foot">${empty ? "选择后保留当前模式和输入位置" : "识别问题意图，按需调用命盘或岁运依据"}</div>
      </section>
      <div class="suggestions">${empty?`<button class="suggestion" data-view="profiles">前往我的档案</button>`:data.suggestions.map(s=>`<button class="suggestion" data-suggestion="${s}">${s}</button>`).join("")}</div>
      <section class="answer" id="answer"><span class="answer-kicker">研判示例 · ${data.label}</span><h3 style="margin-top:8px">先把目标缩小，再选择行动窗口</h3><p class="muted">当前癸卯大运强调学习、方法和稳定积累；2026丙午流年行动性较强。若问题涉及工作变动，先确认岗位与城市，再把决策放到信息充分的节点。</p><div class="evidence-grid"><div class="evidence"><strong>命盘依据</strong><div class="micro">甲木日主 · 午月</div></div><div class="evidence"><strong>岁运依据</strong><div class="micro">癸卯运 · 丙午年</div></div><div class="evidence"><strong>行动建议</strong><div class="micro">先验证，再承诺</div></div></div></section>
    </main>`;
  }

  function modeButton(id, label, ico, disabled) {
    return `<button class="mode-button ${currentMode===id?"active":""}" data-mode="${id}" ${disabled?"disabled":""}>${icon(ico,"sm")}${label}</button>`;
  }

  function profilesView() {
    return `<main class="page">
      ${pageHero("User data · Local first", "我的档案", "管理自己、家人或朋友的出生资料与命盘记录。", `<button class="btn primary" data-view="profile-edit">${icon("plus","sm")} 新建档案</button>`)}
      <section class="panel panel-pad"><div class="section-head"><div><h2>已保存档案</h2><p class="muted">2 份档案 · 当前选择“舒克”</p></div><label style="min-width:280px"><span class="input" style="display:flex;align-items:center;gap:8px">${icon("search","sm")}<input style="border:0;background:transparent;width:100%;outline:0" placeholder="搜索名称、地点或四柱"></span></label></div><div class="profile-grid">${profileCard("舒克","2002年6月15日 11:30 · 女 · 眉山市",["壬午","丙午","甲寅","己巳"],true)}${profileCard("李鸿","2004年5月28日 11:58 · 男 · 四川省",["甲申","己巳","丁未","丙午"],false)}</div></section>
    </main>`;
  }

  function profileCard(name, meta, pillars, selected) {
    return `<article class="profile-card ${selected?"selected":""}"><div class="field-head"><div><h3>${name}</h3><div class="profile-meta">${meta}</div></div>${selected?`<span class="status-chip"><span class="status-dot"></span>当前</span>`:""}</div><div class="mini-pillars">${pillars.map(p=>`<span class="mini-pillar">${p}</span>`).join("")}</div><div class="profile-actions"><button class="btn primary small" data-view="chart-report">查看命盘</button><button class="btn small" data-view="profile-edit">${icon("edit","sm")} 编辑出生资料</button><button class="btn ghost small">删除</button></div></article>`;
  }

  function profileEditView() {
    return `<main class="page">
      ${pageHero("Birth data · 三历同步", "编辑出生资料", "阳历、阴历与四柱由同一排盘引擎换算；地点同时服务于时区与真太阳时。")}
      <section class="panel form-layout">
        <div class="form-column">
          <div class="field"><div class="field-head"><label>档案名称 <span class="required">*</span></label><span class="micro">用于识别档案</span></div><input class="input" value="舒克" aria-label="档案名称"></div>
          <div class="segmented calendar-tabs"><button class="seg-button active" data-calendar="solar">${icon("sun","sm")} 阳历</button><button class="seg-button" data-calendar="lunar">${icon("moon","sm")} 阴历</button><button class="seg-button" data-calendar="pillars">${icon("grid","sm")} 四柱</button></div>
          <div class="wheel" id="date-wheel">${wheelSolar()}</div>
          <p class="micro" id="calendar-note" style="margin:12px 0 0">对应阴历：壬午年五月初五 · 四柱：壬午／丙午／甲寅／己巳</p>
          <div class="field section-gap"><div class="field-head"><label>性别 <span class="required">*</span></label><span class="micro">参与十神与排运</span></div><div class="segmented"><button class="seg-button">男</button><button class="seg-button active">女</button></div></div>
        </div>
        <div class="form-column" style="border-left:1px solid var(--line)">
          <div class="field"><div class="field-head"><label>出生城市 <span class="required">*</span></label><span class="micro">用于时区与经度</span></div><div style="display:grid;grid-template-columns:1fr auto;gap:8px"><input class="input" value="眉山市"><button class="btn">${icon("search","sm")} 检索</button></div></div>
          <div class="map-stage"><span class="map-pin">${icon("map")}</span><span class="micro" style="position:absolute;left:14px;bottom:10px">眉山市 · 103.779001°E</span></div>
          <div class="field section-gap"><div class="field-head"><label>时区 <span class="required">*</span></label><span class="micro">按出生当地民用时间</span></div><button class="select" style="display:flex;align-items:center;justify-content:space-between">${icon("globe","sm")}<span style="margin-right:auto;margin-left:8px">北京（UTC+8）</span>${icon("chevron","sm")}</button></div>
          <div class="field"><div class="field-head"><label>计时方式</label><span class="micro">默认使用所选时区标准时间</span></div><div class="segmented"><button class="seg-button active" data-time="clock">北京时间</button><button class="seg-button" data-time="solar">真太阳时</button></div><div class="coord-card" id="coord-card"><strong>真太阳时定位已就绪</strong><div class="micro">出生地经度 103.779001°E · 修正 -64.9 分钟 · 10:25</div></div></div>
        </div>
        <div class="form-actions"><button class="btn ghost" data-view="profiles">取消</button><button class="btn primary" data-action="save-profile">保存档案 ${icon("arrow","sm")}</button></div>
      </section>
    </main>`;
  }

  function wheelSolar() {
    return [["年","2001","2002","2003"],["月","05","06","07"],["日","14","15","16"],["时","10","11","12"],["分","29","30","31"]].map(x=>`<div class="wheel-col"><small>${x[0]}</small><span>${x[1]}</span><strong>${x[2]}</strong><span>${x[3]}</span></div>`).join("");
  }
  function wheelLunar() {
    return [["年","2001","2002","2003"],["月","四月","五月","六月"],["日","初四","初五","初六"],["时","巳时","午时","未时"],["分","二十九","三十","三十一"]].map(x=>`<div class="wheel-col"><small>${x[0]}</small><span>${x[1]}</span><strong>${x[2]}</strong><span>${x[3]}</span></div>`).join("");
  }
  function wheelPillars() {
    return [["年柱","辛巳","壬午","癸未"],["月柱","乙巳","丙午","丁未"],["日柱","癸丑","甲寅","乙卯"],["时柱","戊辰","己巳","庚午"]].map(x=>`<div class="wheel-col" style="grid-column:auto"><small>${x[0]}</small><span>${x[1]}</span><strong>${x[2]}</strong><span>${x[3]}</span></div>`).join("")+`<div class="wheel-col"><small>匹配</small><span>上一组</span><strong>2 组</strong><span>下一组</span></div>`;
  }

  function principlesView() {
    return `<main class="page">
      ${pageHero("Principles · 产品约定", "玄衡如何给出判断", "设计不是装饰：每个页面都围绕可核验排盘、可追溯依据与可执行建议。")}
      <section class="principle-grid"><article class="principle"><h2>计算先于解释</h2><p class="muted">三历换算、真太阳时、四柱、大运、流年和节气流月先由确定性引擎计算，再交给模型组织语言。</p></article><article class="principle"><h2>时间必须可核验</h2><p class="muted">所有时间结论都展示时区、经度、修正结果或节气边界，避免把阳历自然月误作传统流月。</p></article><article class="principle"><h2>建议服从现实</h2><p class="muted">研判提供参考与行动窗口，不替代医疗、法律、财务等专业判断，也不制造确定性承诺。</p></article></section>
      <section class="panel panel-pad section-gap"><div class="section-head"><div><h2>统一术语</h2><p class="muted">同一个对象只使用一个名字。</p></div></div><table class="glossary"><thead><tr><th>对象</th><th>统一称呼</th><th>使用位置</th></tr></thead><tbody><tr><td>用户保存的出生记录</td><td>档案</td><td>我的档案、当前档案</td></tr><tr><td>日期、时间、城市等</td><td>出生资料</td><td>新建与编辑</td></tr><tr><td>排盘与结构解释</td><td>命盘报告</td><td>命盘研判</td></tr><tr><td>大运、流年、流月</td><td>岁运时间轴</td><td>时间趋势</td></tr><tr><td>模型问答工作台</td><td>问一件事</td><td>随缘、看运、倾听、问事</td></tr></tbody></table></section>
    </main>`;
  }

  function drawer() {
    return `<div class="drawer-overlay" data-action="drawer-close"></div><aside class="prototype-drawer" aria-label="十页原型目录"><div class="drawer-head"><div><div class="eyebrow">Prototype set</div><h3>${theme.name}</h3><div class="micro">${theme.note}</div></div><button class="btn small" data-action="drawer-close">${icon("x")}</button></div><div class="drawer-list">${pages.map((p,i)=>`<button class="drawer-item ${currentView===p[0]?"active":""}" data-view="${p[0]}"><span class="num">${String(i+1).padStart(2,"0")}</span><span><strong>${p[1]}</strong><small style="display:block">${p[2]}</small></span>${icon(iconNames[p[0].split("-")[0]]||"arrow","sm")}</button>`).join("")}</div></aside>`;
  }

  function render() {
    const app = document.getElementById("app");
    const view = currentView === "home" ? homeView() : currentView === "chart-empty" ? emptyView("chart") : currentView === "chart-report" ? chartView() : currentView === "timing-empty" ? emptyView("timing") : currentView === "timing" ? timingView() : currentView === "question-empty" ? questionView(true) : currentView === "question" ? questionView(false) : currentView === "profiles" ? profilesView() : currentView === "profile-edit" ? profileEditView() : principlesView();
    app.innerHTML = sprite() + `<div class="app-shell">${header()}${view}</div>${drawer()}<div class="toast" id="toast"></div>`;
    document.title = `玄衡 · ${routeMap.get(currentView).title} · ${theme.name}`;
    bind();
  }

  function setView(id) {
    if (!routeMap.has(id)) return;
    currentView = id;
    history.replaceState(null, "", `#${id}`);
    render();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function bind() {
    document.querySelectorAll("[data-view]").forEach(el => el.addEventListener("click", () => setView(el.dataset.view)));
    document.querySelectorAll("[data-action='drawer']").forEach(el => el.addEventListener("click", openDrawer));
    document.querySelectorAll("[data-action='drawer-close']").forEach(el => el.addEventListener("click", closeDrawer));
    document.querySelectorAll("[data-mode]").forEach(el => el.addEventListener("click", () => { currentMode = el.dataset.mode; render(); }));
    document.querySelectorAll("[data-suggestion]").forEach(el => el.addEventListener("click", () => { const input = document.getElementById("question-input"); if (input) { input.value = el.dataset.suggestion; input.focus(); } }));
    document.querySelectorAll("[data-action='ask']").forEach(el => el.addEventListener("click", () => { const answer = document.getElementById("answer"); if (answer) { answer.classList.add("show"); answer.scrollIntoView({ behavior: "smooth", block: "nearest" }); } }));
    document.querySelectorAll("[data-action='years']").forEach(el => el.addEventListener("click", () => { expandedYears = !expandedYears; render(); }));
    document.querySelectorAll("[data-action='months']").forEach(el => el.addEventListener("click", () => { expandedMonths = !expandedMonths; render(); }));
    document.querySelectorAll("[data-calendar]").forEach(el => el.addEventListener("click", () => changeCalendar(el.dataset.calendar)));
    document.querySelectorAll("[data-time]").forEach(el => el.addEventListener("click", () => changeTimeMode(el)));
    document.querySelectorAll("[data-action='save-profile']").forEach(el => el.addEventListener("click", () => { showToast("档案已更新，未创建重复记录"); setTimeout(() => setView("profiles"), 700); }));
    document.querySelectorAll("[data-action='luck']").forEach(el => el.addEventListener("click", () => { document.querySelectorAll(".luck-card").forEach(x=>x.classList.remove("active")); el.classList.add("active"); }));
    document.querySelectorAll(".year-card").forEach(el => el.addEventListener("click", () => { document.querySelectorAll(".year-card").forEach(x=>x.classList.remove("active")); el.classList.add("active"); }));
    document.querySelectorAll(".month-card").forEach(el => el.addEventListener("click", () => { document.querySelectorAll(".month-card").forEach(x=>x.classList.remove("active")); el.classList.add("active"); }));
  }

  function openDrawer() { document.querySelector(".prototype-drawer")?.classList.add("open"); document.querySelector(".drawer-overlay")?.classList.add("show"); }
  function closeDrawer() { document.querySelector(".prototype-drawer")?.classList.remove("open"); document.querySelector(".drawer-overlay")?.classList.remove("show"); }
  function showToast(message) { const toast = document.getElementById("toast"); if (!toast) return; toast.textContent = message; toast.classList.add("show"); setTimeout(()=>toast.classList.remove("show"), 1500); }

  function changeCalendar(type) {
    document.querySelectorAll("[data-calendar]").forEach(x=>x.classList.toggle("active", x.dataset.calendar===type));
    const wheel = document.getElementById("date-wheel");
    const note = document.getElementById("calendar-note");
    if (!wheel || !note) return;
    if (type === "solar") { wheel.innerHTML = wheelSolar(); note.textContent = "对应阴历：壬午年五月初五 · 四柱：壬午／丙午／甲寅／己巳"; }
    if (type === "lunar") { wheel.innerHTML = wheelLunar(); note.textContent = "对应阳历：2002年6月15日 11:30 · 四柱：壬午／丙午／甲寅／己巳"; }
    if (type === "pillars") { wheel.innerHTML = wheelPillars(); note.textContent = "当前四柱匹配 2 个出生时间；选择后将同步回阳历与阴历。"; }
  }

  function changeTimeMode(el) {
    document.querySelectorAll("[data-time]").forEach(x=>x.classList.toggle("active", x===el));
    document.getElementById("coord-card")?.classList.toggle("show", el.dataset.time === "solar");
  }

  const initial = location.hash.replace("#", "");
  if (routeMap.has(initial)) currentView = initial;
  window.addEventListener("hashchange", () => {
    const next = location.hash.replace("#", "");
    if (routeMap.has(next) && next !== currentView) { currentView = next; render(); }
  });
  render();
})();
