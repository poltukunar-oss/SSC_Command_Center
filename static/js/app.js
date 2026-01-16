async function loadNews(source, elementId){
  try{
    const res = await fetch(`/api/news/${source}`);
    const data = await res.json();

    document.getElementById(elementId).innerHTML =
      data.map(n=>`<li>▸ <a href="${n.link}" target="_blank">${n.title}</a></li>`).join("");
  }catch(e){
    document.getElementById(elementId).innerHTML = "<li>Unable to load news</li>";
  }
}

async function loadCurrentAffairs(){
  try{
    const res = await fetch("/api/current_affairs");
    const data = await res.json();

    document.getElementById("daily-ca").innerHTML =
      data.map(n=>`<li>🔹 <b>[${n.source.toUpperCase()}]</b> 
      <a href="${n.link}" target="_blank">${n.title}</a></li>`).join("");
  }catch(e){
    document.getElementById("daily-ca").innerHTML="<li>Unable to load current affairs</li>";
  }
}

function loadAllNews(){
  loadNews("reuters","reuters-news");
  loadNews("thehindu","hindu-news");
  loadNews("pib","pib-news");
  loadCurrentAffairs();
}

loadAllNews();

/* auto refresh every 30 min */
setInterval(loadAllNews,1800000);
async function loadNews(src,id){
 const r=await fetch(`/api/news/${src}`); const d=await r.json();
 document.getElementById(id).innerHTML=d.map(n=>`<li>▸ <a href="${n.link}" target="_blank">${n.title}</a></li>`).join("");
}

async function loadCA(){
 const r=await fetch("/api/current_affairs"); const d=await r.json();
 document.getElementById("daily-ca").innerHTML=d.map(n=>`<li>🔹 <b>[${n.source.toUpperCase()}]</b> <a href="${n.link}" target="_blank">${n.title}</a></li>`).join("");
}

async function getNewFact(){
 document.getElementById("fact-text").innerText="Loading SSC fact...";
 const r=await fetch("/api/daily_fact"); const d=await r.json();
 document.getElementById("fact-text").innerText=d.fact;
}

function loadAll(){
 loadNews("reuters","reuters-news");
 loadNews("thehindu","hindu-news");
 loadNews("pib","pib-news");
 loadCA();
 getNewFact();
}

loadAll();
setInterval(loadAll,1800000);
