const canvas = document.getElementById("verifyCanvas");
const ctx = canvas.getContext("2d");

ctx.lineWidth = 2;
ctx.lineCap = "round";
ctx.strokeStyle = "#0b3d91";

let drawing = false;

let signatureData = [];
let currentStroke = [];
let strokeID = 0;

let customerLoaded = false;
let customerID = null;

function getPosition(e) {

    const rect = canvas.getBoundingClientRect();

    const scaleX = canvas.width / rect.width;
    const scaleY = canvas.height / rect.height;

    return {

        x: (e.clientX - rect.left) * scaleX,

        y: (e.clientY - rect.top) * scaleY

    };

}

canvas.addEventListener("pointerdown", (e) => {

    if (!customerLoaded) {
        alert("Load customer first.");
        return;
    }

    drawing = true;
    strokeID++;
    currentStroke = [];

    const pos = getPosition(e);

    ctx.beginPath();
    ctx.moveTo(pos.x, pos.y);

});

canvas.addEventListener("pointermove", (e) => {

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

canvas.addEventListener("pointerup", () => {

    drawing = false;

    if (currentStroke.length > 0)
        signatureData.push(currentStroke);

});

document.getElementById("clearBtn").onclick = () => {

    ctx.clearRect(0, 0, canvas.width, canvas.height);

    signatureData = [];
    currentStroke = [];
    strokeID = 0;

};

document.getElementById("loadBtn").onclick = async () => {

    const account = document.getElementById("accountNumber").value.trim();

    if (account === "") {
        alert("Enter Account Number");
        return;
    }

    const loadBtn = document.getElementById("loadBtn");

    loadBtn.disabled = true;
    loadBtn.innerHTML = "Loading...";

    try {

        const response = await fetch("/load_customer", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                account: account
            })
        });

        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return;
        }

        customerLoaded = true;
        customerID = result.customer_id;

        document.getElementById("customerName").innerHTML =
            "Customer : " + result.name;

        document.getElementById("status").innerHTML =
            "Status : Reference Loaded ✓";

        document.getElementById("verifyBtn").disabled = false;

    } catch (error) {

        console.error(error);
        alert("Unable to load customer.");

    } finally {

        loadBtn.disabled = false;
        loadBtn.innerHTML = "Load Customer";

    }

};

document.getElementById("verifyBtn").onclick = async () => {

    if (signatureData.length === 0) {
        alert("Draw the test signature.");
        return;
    }

    const verifyButton = document.getElementById("verifyBtn");

    verifyButton.disabled = true;
    verifyButton.innerHTML = "Verifying...";

    try {

        const response = await fetch("/verify_signature", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                customer_id: customerID,
                signature: signatureData
            })
        });

        const result = await response.json();

        if (!result.success) {
            alert(result.message);
            return;
        }

        showResult(result);

    } catch (error) {

        console.error(error);
        alert("Verification failed. Please try again.");

    } finally {

        verifyButton.disabled = false;
        verifyButton.innerHTML = "Verify Signature";

    }

};

let chart = null;
let pdfPath = "";

function showResult(result) {

    document.getElementById("resultCard").style.display = "block";

    const decision = document.getElementById("decisionValue");

decision.innerHTML = result.decision;

decision.style.fontWeight = "700";

decision.style.color = "#ffffff";

if(result.decision === "Authentic"){

    decision.style.background = "#16a34a";

}

else if(result.decision === "Forgery"){

    decision.style.background = "#dc2626";

}

else{

    decision.style.background = "#ca8a04";

}

    document.getElementById("confidenceValue").innerHTML =
        result.confidence.toFixed(2) + "%";

    document.getElementById("similarityValue").innerHTML =
        result.similarity.toFixed(2) + "%";

        pdfPath = result.pdf;

    document.getElementById("confidenceBar").style.width =
    result.confidence + "%";

document.getElementById("similarityBar").style.width =
    result.similarity + "%";


const risk = document.getElementById("riskValue");

if(result.decision === "Authentic"){

    risk.innerHTML = "🟢 Low Risk";
    risk.style.color = "#16a34a";

}

else if(result.decision === "Forgery"){

    risk.innerHTML = "🔴 High Risk";
    risk.style.color = "#dc2626";

}

else{

    risk.innerHTML = "🟡 Human Verification";
    risk.style.color = "#ca8a04";

}

    buildComparisonTable(
        result.reference_features,
        result.test_features
    );

    buildChart(
        result.reference_features,
        result.test_features
    );
buildExplanation(
    result.reference_features,
    result.test_features
);
}

function buildComparisonTable(reference, test) {

    const tbody = document.querySelector("#comparisonTable tbody");

    tbody.innerHTML = "";

    Object.keys(reference).forEach(feature => {

        const ref = Number(reference[feature]);

        const tst = Number(test[feature]);

        const difference = Math.abs(ref - tst);

        let status = "";
        let color = "";

        if (difference <= ref * 0.10) {

            status = "✅ PASS";
            color = "#16a34a";

        }

        else if (difference <= ref * 0.25) {

            status = "🟡 CLOSE";
            color = "#ca8a04";

        }

        else {

            status = "❌ FAIL";
            color = "#dc2626";

        }

        let badgeClass = "";

if(status.includes("PASS")){

    badgeClass = "pass";

}

else if(status.includes("CLOSE")){

    badgeClass = "close";

}

else{

    badgeClass = "fail";

}

tbody.innerHTML += `

<tr>

    <td>${feature}</td>

    <td>${ref.toFixed(2)}</td>

    <td>${tst.toFixed(2)}</td>

    <td>

        <span class="status-badge ${badgeClass}">

            ${status}

        </span>

    </td>

</tr>

`;

    });

}
function buildChart(reference, test) {

    const labels = Object.keys(reference);

    const refValues = Object.values(reference);

    const testValues = Object.values(test);

    if (chart)
        chart.destroy();

    chart = new Chart(

        document.getElementById("comparisonChart"),

        {

            type: "line",

            data: {

                labels: labels,

                datasets: [

                    {

                        label: "Reference",

                        data: refValues,

                        borderWidth: 3

                    },

                    {

                        label: "Test",

                        data: testValues,

                        borderWidth: 3

                    }

                ]

            },

            options: {

                responsive: true,

                animation: {

                    duration: 1500

                }

            }

        }

    );

}



function buildExplanation(reference, test){

    const list =
        document.getElementById("analysisList");

    list.innerHTML = "";

    Object.keys(reference).forEach(feature=>{

        const ref = Number(reference[feature]);

        const tst = Number(test[feature]);

        const difference = Math.abs(ref - tst);

        const percentage =
            (difference / Math.max(Math.abs(ref),1))*100;

        let message="";

        if(percentage<=10){

            message=
            "✅ " + feature +
            " matches the enrolled signature.";

        }

        else if(percentage<=25){

            message=
            "🟡 " + feature +
            " shows normal variation.";

        }

        else{

            message=
            "❌ " + feature +
            " differs significantly.";

        }

        list.innerHTML +=
        "<li>"+message+"</li>";

    });

}

document.getElementById("pdfBtn").onclick = () => {

    if (!pdfPath) {

        alert("No PDF available.");

        return;

    }

    window.open("/" + pdfPath, "_blank");

};

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

async function checkUploadedSignature() {

    try {

        const response = await fetch("/signature/get");
        const result = await response.json();

        if (!result.updated)
            return;

        signatureData = result.signature;

        drawSignature(signatureData);

        await fetch("/signature/clear", {
            method: "POST"
        });

        console.log("Signature imported from phone.");

    }
    catch (err) {

        console.error(err);

    }

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

    return getServerAddress() + "/signature-pad?mode=verify";

}

let connectionTimer = null;

function showQRCode() {

    qrModal.style.display = "flex";

    const qrContainer = document.getElementById("qrCode");

    qrContainer.innerHTML = "";

    new QRCode(qrContainer, {
        text: buildSignatureURL(),
        width: 220,
        height: 220
    });
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
    function (e) {

        if (e.target === qrModal) {
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

clearInterval(window.signaturePoller);

window.signaturePoller = null;

        await fetch("/signature/clear", {
            method: "POST"
        });

    }
    catch (err) {

        console.error(err);

    }

}