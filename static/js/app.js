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
