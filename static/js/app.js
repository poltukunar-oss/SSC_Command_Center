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
const examDate = new Date("September 1, 2026 09:00:00").getTime();
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
function startExamCountdown() {
    // Target Date: 1 September 2026
    const targetDate = new Date("September 1, 2026 00:00:00").getTime();

    const timerInterval = setInterval(() => {
        const now = new Date().getTime();
        const difference = targetDate - now;

        // Time calculations
        const days = Math.floor(difference / (1000 * 60 * 60 * 24));
        const hours = Math.floor((difference % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        const minutes = Math.floor((difference % (1000 * 60 * 60)) / (1000 * 60));
        const seconds = Math.floor((difference % (1000 * 60)) / 1000);

        // UI Update
        const display = document.getElementById("countdown-timer");
        
        if (display) {
            display.innerHTML = `${days}d ${hours}h ${minutes}m ${seconds}s`;
        }

        // Agar date aa gayi toh stop kar do
        if (difference < 0) {
            clearInterval(timerInterval);
            if (display) display.innerHTML = "EXAM DAY!";
        }
    }, 1000); // Har 1 second (1000ms) mein update hoga
}

// Function ko call karo
startExamCountdown();