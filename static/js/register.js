const canvas = document.getElementById("signatureCanvas");



const ctx = canvas.getContext("2d");

ctx.lineWidth = 2;
ctx.lineCap = "round";
ctx.strokeStyle = "#0b3d91";


let drawing = false;
let sample = 1;

let signatureData = [];
let currentStroke = [];
let strokeID = 0;

// Stores all 3 signatures
let references = [];

function getPosition(e) {

    const rect = canvas.getBoundingClientRect();

    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {
        x: (e.clientX - rect.left) * scaleX,
        y: (e.clientY - rect.top) * scaleY
    };

}

canvas.addEventListener("pointerdown", function (e) {

    drawing = true;

    strokeID++;

    currentStroke = [];

    const pos = getPosition(e);

    ctx.beginPath();

    ctx.moveTo(pos.x, pos.y);

});

canvas.addEventListener("pointermove", function (e) {

    if (!drawing) return;

    const pos = getPosition(e);

    ctx.lineTo(pos.x, pos.y);

    ctx.stroke();

    currentStroke.push({

        x: pos.x,

        y: pos.y,

        time: Date.now(),

        pressure: e.pressure || 0.5,

        stroke: strokeID

    });

});

canvas.addEventListener("pointerup", function () {

    drawing = false;

    if (currentStroke.length > 0) {
        signatureData.push(currentStroke);
    }

});

canvas.addEventListener("pointerleave", function () {

    drawing = false;

});

document.getElementById("clearBtn").addEventListener("click", function () {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    signatureData = [];
    currentStroke = [];
    strokeID = 0;

});

document.getElementById("saveBtn").addEventListener("click", function () {

    if (signatureData.length === 0) {

        alert("Please draw a signature first.");

        return;

    }

    references.push(signatureData);

    if (sample < 3) {

        sample++;

        document.getElementById("sampleCounter").innerText = sample;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        signatureData = [];
        currentStroke = [];
        strokeID = 0;

    }
    else {

        document.getElementById("registerBtn").disabled = false;

        alert("All 3 signatures captured.\nClick Register Customer.");

    }

});

document.getElementById("registerBtn").addEventListener("click", async function () {

    const name = document.getElementById("customerName").value.trim();
    const account = document.getElementById("accountNumber").value.trim();

    if (name === "" || account === "") {
        alert("Please enter customer details.");
        return;
    }

    const registerBtn = document.getElementById("registerBtn");

    registerBtn.disabled = true;
    registerBtn.innerText = "Registering...";

    try {

        const response = await fetch("/save_customer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                name: name,
                account: account,
                reference1: references[0],
                reference2: references[1],
                reference3: references[2]
            })
        });

        const result = await response.json();

        if (result.success) {

            alert("Customer Registered Successfully!");
            window.location.href = "/";

        } else {

            alert(result.message || "Customer registration failed.");

        }

    } catch (error) {

        console.error(error);
        alert("Unable to connect to the server.");

    } finally {

        registerBtn.disabled = false;
        registerBtn.innerText = "Register Customer";

    }

});

function drawSignature(data) {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    if (!Array.isArray(data))
        return;

    data.forEach(stroke => {

        if (!Array.isArray(stroke) || stroke.length === 0)
            return;

        ctx.beginPath();

        ctx.moveTo(stroke[0].x, stroke[0].y);

        for (let i = 1; i < stroke.length; i++) {

            ctx.lineTo(
                stroke[i].x,
                stroke[i].y
            );

        }

        ctx.stroke();

    });

}



/* ==========================================================
   Mobile Signature Pad
========================================================== */

const mobilePadBtn = document.getElementById("mobilePadBtn");
const qrModal = document.getElementById("qrModal");
const closeQR = document.getElementById("closeQR");

function getServerAddress() {

    return window.location.origin;

}

function buildSignatureURL() {

    return getServerAddress() + "/signature-pad?mode=register";

}

let connectionTimer = null;

function showQRCode() {

    qrModal.style.display = "flex";

    const qrContainer = document.getElementById("qrCode");

    qrContainer.innerHTML = "";

    new QRCode(

        qrContainer,

        {

            text: buildSignatureURL(),

            width: 220,

            height: 220

        }

    );

}

connectionTimer = setInterval(
    checkMobileConnection,
    1000
);

function hideQRCode() {

    qrModal.style.display = "none";

    if (connectionTimer) {

        clearInterval(connectionTimer);

        connectionTimer = null;

    }

    fetch("/signature/status")
        .then(response => response.json())
        .then(result => {

            if (!result.connected) {

                mobilePadBtn.innerHTML = "📱 Mobile Signature";

                mobilePadBtn.disabled = false;

            }

        });

}


mobilePadBtn.addEventListener(

    "click",

    showQRCode

);

closeQR.addEventListener(

    "click",

    hideQRCode

);

window.addEventListener(

    "click",

    function(e){

        if(e.target===qrModal){

            hideQRCode();

        }

    }

);

async function checkMobileConnection() {

    try {

        const response = await fetch("/signature/status");

        const result = await response.json();

        if (result.connected) {

            hideQRCode();

mobilePadBtn.innerHTML = "🟢 Mobile Connected";

mobilePadBtn.disabled = true;

if (!window.signaturePoller) {

    window.signaturePoller =
        setInterval(checkUploadedSignature, 500);

}


        }

    }
    catch (err) {

        console.error(err);

    }

}

async function checkUploadedSignature() {

    try {

        const response = await fetch("/signature/get");
        const result = await response.json();

        if (!result.updated)
            return;

        console.log("Signature received from phone");

        signatureData = result.signature;

        drawSignature(signatureData);

references.push(signatureData);

if (sample < 3) {

    sample++;

    document.getElementById("sampleCounter").innerText = sample;

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    signatureData = [];
    currentStroke = [];
    strokeID = 0;

    await fetch("/signature/clear", {
        method: "POST"
    });

    return;

}

// Third sample

document.getElementById("registerBtn").disabled = false;

await fetch("/signature/clear", {
    method: "POST"
});

clearInterval(window.signaturePoller);

window.signaturePoller = null;

alert("All 3 signatures captured.\nClick Register Customer.");

    }
    catch (err) {

        console.error(err);

    }

}


