const complaintBox = document.getElementById("complaint");
const submitBtn = document.getElementById("submitBtn");
const voiceBtn = document.getElementById("voiceBtn");
const result = document.getElementById("result");
const languageSelect = document.getElementById("language");

let mediaRecorder;
let audioChunks = [];
let isRecording = false;


// ============================================
// VOICE RECORDING
// ============================================

voiceBtn.addEventListener("click", async function () {

    // If already recording → STOP
    if (isRecording) {

        mediaRecorder.stop();

        isRecording = false;

        voiceBtn.innerText = "🎙️ Processing...";

        return;
    }


    // Ask browser for microphone access
    try {

        const stream =
            await navigator.mediaDevices.getUserMedia({
                audio: true
            });


        // Create recorder
        mediaRecorder =
            new MediaRecorder(stream);

        audioChunks = [];


        // When audio data arrives
        mediaRecorder.ondataavailable = function (event) {

            if (event.data.size > 0) {

                audioChunks.push(event.data);
            }
        };


        // When recording stops
        mediaRecorder.onstop = async function () {

            // Stop microphone
            stream.getTracks().forEach(track => {
                track.stop();
            });


            // Create audio file
            const audioBlob =
                new Blob(
                    audioChunks,
                    { type: "audio/webm" }
                );


            // Send audio to Whisper
            await sendAudioToWhisper(audioBlob);
        };


        // Start recording
        mediaRecorder.start();

        isRecording = true;

        voiceBtn.innerText =
            "🔴 Recording... Click to Stop";


    } catch (error) {

        console.error("Microphone error:", error);

        alert(
            "Could not access microphone. " +
            "Please allow microphone permission."
        );
    }
});


// ============================================
// SEND AUDIO TO WHISPER
// ============================================

async function sendAudioToWhisper(audioBlob) {

    try {

        voiceBtn.innerText =
            "🤖 Whisper is processing...";


        // Create form data
        const formData = new FormData();

        formData.append(
            "file",
            audioBlob,
            "complaint.webm"
        );
        formData.append(
    "language",
    languageSelect.value
);


        // Send to FastAPI
        const response =
            await fetch(
                "http://127.0.0.1:8000/transcribe",
                {
                    method: "POST",
                    body: formData
                }
            );


        // Check server response
        if (!response.ok) {

            throw new Error(
                "Server returned error: " +
                response.status
            );
        }


        const data =
            await response.json();


        console.log("Whisper response:", data);


        // Put transcription into textbox
        complaintBox.value =
            data.text;


        voiceBtn.innerText =
            "🎙️ Speak Complaint";


        console.log(
            "Detected language:",
            data.language
        );


    } catch (error) {

        console.error(
            "Whisper error:",
            error
        );


        voiceBtn.innerText =
            "🎙️ Try Again";


        alert(
            "Could not process the audio. " +
            "Check that the Whisper server is running."
        );
    }
}


// ============================================
// SUBMIT COMPLAINT
// ============================================

submitBtn.addEventListener("click", async function () {

    const complaint = complaintBox.value.trim();

    if (complaint === "") {
        alert("Please enter or speak your complaint.");
        return;
    }

    submitBtn.innerText = "🤖 Analyzing Complaint...";

    try {

        const formData = new FormData();
        formData.append("complaint", complaint);

        console.log("Sending complaint:", complaint);

        const response = await fetch(
            "http://127.0.0.1:8000/analyze",
            {
                method: "POST",
                body: formData
            }
        );

        console.log("HTTP Status:", response.status);

        const rawResponse = await response.text();

        console.log("Backend Response:", rawResponse);

        if (!response.ok) {
            throw new Error(
                `Backend error ${response.status}: ${rawResponse}`
            );
        }

        const data = JSON.parse(rawResponse);

        console.log("Parsed AI Analysis:", data);

        result.style.display = "block";

        result.innerHTML = `
            <h3>Complaint Analysis 🤖</h3>

            <p>
                <strong>Complaint:</strong>
                ${data.original_text || complaint}
            </p>

            <hr>

            <p>
                <strong>Category:</strong>
                ${data.category || "Not detected"}
            </p>

            <p>
                <strong>Department:</strong>
                ${data.department || "Not detected"}
            </p>

            <p>
                <strong>Priority:</strong>
                ${data.priority || "Not detected"}
            </p>

            <br>

            <p>
                <strong>Status:</strong>
                Ready for Submission
            </p>
        `;

    }

    catch (error) {

        console.error("❌ Analysis error:", error);

        result.style.display = "block";

        result.innerHTML = `
            <h3>❌ Analysis Failed</h3>

            <p>
                ${error.message}
            </p>
        `;

    }

    finally {

        submitBtn.innerText = "Submit Complaint";

    }

});