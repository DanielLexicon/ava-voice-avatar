const startLiveAvatarBtn = document.getElementById("startLiveAvatarBtn");
const liveAvatarStatus = document.getElementById("liveAvatarStatus");
const liveAvatarVideo = document.getElementById("liveAvatarVideo");
const liveAvatarPlaceholder = document.getElementById("liveAvatarPlaceholder");

async function startLiveAvatarTest() {
    liveAvatarStatus.textContent = "Solicitando session token de LiveAvatar...";
    startLiveAvatarBtn.disabled = true;

    try {
        const response = await fetch("/api/liveavatar/session-token");
        const data = await response.json();

        if (!response.ok) {
            liveAvatarStatus.textContent = "Error creando session token.";
            console.error("LiveAvatar error:", data);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        console.log("LiveAvatar session data:", data);

        const sessionId = data?.data?.session_id;
        const sessionToken = data?.data?.session_token;

        if (!sessionId || !sessionToken) {
            liveAvatarStatus.textContent = "LiveAvatar respondió, pero faltan session_id o session_token.";
            startLiveAvatarBtn.disabled = false;
            return;
        }

        liveAvatarStatus.textContent = "Session token recibido. Falta conectar el SDK de video.";
        liveAvatarPlaceholder.textContent = "Session creada correctamente. Ahora falta conectar WebRTC/SDK.";
    } catch (error) {
        liveAvatarStatus.textContent = "Error conectando con LiveAvatar.";
        console.error(error);
        startLiveAvatarBtn.disabled = false;
    }
}

if (startLiveAvatarBtn) {
    startLiveAvatarBtn.addEventListener("click", startLiveAvatarTest);
}