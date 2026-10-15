/*
=========================================================
Mobile Signature Pad
Part 1
LOCKED
=========================================================
*/

const canvas = document.getElementById("mobileCanvas");
const ctx = canvas.getContext("2d");

const params = new URLSearchParams(window.location.search);

const mode = params.get("mode") || "verify";

const pageTitle = document.getElementById("pageTitle");

const actionBtn = document.getElementById("actionBtn");


let sample = 1;

if (mode === "register") {

    pageTitle.innerHTML = "Sample 1 / 3";

    actionBtn.innerHTML = "💾 Save Sample";

}
else {

    pageTitle.innerHTML = "Signature Pad";

    actionBtn.innerHTML = "✓ Done";

}

let drawing = false;

let signatureData = [];

let currentStroke = [];

function resizeCanvas() {

    if (window.innerHeight > window.innerWidth) {
        return;
    }

    const header = document.querySelector(".mobile-header");

    const canvasHeight =
        window.innerHeight -
        header.offsetHeight;

    canvas.width = window.innerWidth;

    canvas.height = canvasHeight;

    canvas.style.width = "100%";

    canvas.style.height = canvasHeight + "px";

    ctx.lineWidth = 2.5;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.strokeStyle = "#0d6efd";

}

async function notifyConnected() {

    try {

        await fetch("/signature/connect", {
            method: "POST"
        });

    }
    catch (err) {

        console.error("Connection failed:", err);

    }

}

window.addEventListener("resize", resizeCanvas);

resizeCanvas();

notifyConnected();

function getPoint(e) {

    const rect = canvas.getBoundingClientRect();

    let clientX;
    let clientY;

    if (e.touches && e.touches.length > 0) {

        clientX = e.touches[0].clientX;
        clientY = e.touches[0].clientY;

    } else {

        clientX = e.clientX;
        clientY = e.clientY;

    }

    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {

        x: (clientX - rect.left) * scaleX,

        y: (clientY - rect.top) * scaleY,

        pressure: e.pressure || 0.5,

        time: Date.now()

    };

}

function startDraw(e) {

    e.preventDefault();

    drawing = true;

    currentStroke = [];

    const p = getPoint(e);

    currentStroke.push(p);

    ctx.beginPath();

    ctx.moveTo(p.x, p.y);

}

function draw(e) {

    if (!drawing) return;

    e.preventDefault();

    const p = getPoint(e);

    currentStroke.push(p);

    ctx.lineTo(p.x, p.y);

    ctx.stroke();

}

function endDraw(e) {

    if (!drawing) return;

    drawing = false;

    signatureData.push(currentStroke);

}

canvas.addEventListener("pointerdown", startDraw);

canvas.addEventListener("pointermove", draw);

canvas.addEventListener("pointerup", endDraw);

canvas.addEventListener("pointerleave", endDraw);

canvas.addEventListener("pointercancel", endDraw);

document.getElementById("clearBtn").addEventListener(

    "click",

    function () {

        ctx.clearRect(

            0,

            0,

            canvas.width,

            canvas.height

        );

        signatureData = [];

    }

);


/* ==========================================================
   Upload Signature
========================================================== */

document
    .getElementById("actionBtn")
    .addEventListener(
        "click",
        async function () {

            if (signatureData.length === 0) {
                alert("Please draw your signature.");
                return;
            }

            const doneBtn = document.getElementById("actionBtn");

            doneBtn.disabled = true;
            doneBtn.textContent = "Sending...";

            try {

                const response = await fetch(
                    "/signature/upload",
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json"
                        },
                        body: JSON.stringify({
                            signature: signatureData
                        })
                    }
                );

                const result = await response.json();

                if (result.success) {

    if (mode === "register") {

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        signatureData = [];
        currentStroke = [];

        if (sample < 3) {

            sample++;

            pageTitle.innerHTML = "Sample " + sample + " / 3";

        }
        else {

            pageTitle.innerHTML = "All Samples Captured";

            actionBtn.disabled = true;

            actionBtn.innerHTML = "✓ Completed";

        }

    }
    else {

        alert("Signature sent successfully.");

    }

}
     else {
                    alert(result.message || "Upload failed.");
                }

            } catch (error) {

                console.error(error);
                alert("Unable to send signature.");

            } finally {

                doneBtn.disabled = false;
                doneBtn.textContent = "Done";

            }

        }
    );

    window.addEventListener("beforeunload", () => {

    navigator.sendBeacon("/signature/disconnect");

});