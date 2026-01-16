console.log("SSC Command Center JS Loaded 🚀");

/* --------- HELPERS ---------- */

function notify(msg){
    alert(msg);
}

/* --------- PAGE READY ---------- */

document.addEventListener("DOMContentLoaded",()=>{
    console.log("Dashboard Ready ✅");
});

/* --------- FUTURE EXTENSIONS ---------- */

/*
Yahin pe baad me add honge:
- daily targets
- analytics
- reminders
- pdf export
- ai analysis
*/
// 1. Countdown Logic (Set your exam date here)
const examDate = new Date("November 29, 2025 09:00:00").getTime();
setInterval(() => {
    const now = new Date().getTime();
    const diff = examDate - now;
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    document.getElementById("countdown").innerHTML = days + " Days to Go!";
}, 1000);

// 2. Daily Flashcards (Based on CGL 2025 Analysis)
const facts = [
    "BNS Section 103 replaces IPC Section 302 for Murder.",
    "Goncha Festival is celebrated in Bastar, Chhattisgarh.",
    "Svaravalis are the basic exercises in Carnatic Music.",
    "Article 44 of the Constitution relates to Uniform Civil Code.",
    "Bharatiya Nagarik Suraksha Sanhita (BNSS) replaces the CrPC."
];

function getNewFact() {
    const randomFact = facts[Math.floor(Math.random() * facts.length)];
    document.getElementById("fact-text").innerText = randomFact;
}

// Initial call to show a fact
getNewFact();