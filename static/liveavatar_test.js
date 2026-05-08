const startLiveAvatarBtn = document.getElementById("startLiveAvatarBtn");
const liveAvatarStatus = document.getElementById("liveAvatarStatus");
const liveAvatarVideo = document.getElementById("liveAvatarVideo");
const liveAvatarPlaceholder = document.getElementById("liveAvatarPlaceholder");

let liveAvatar = null;

async function startLiveAvatarTest() {
    liveAvatarStatus.textContent = "Solicitando session token de LiveAvatar...";
    startLiveAvatarBtn.disabled = true;

    try {
        const response = await fetch("/api/liveavatar/session-token");
        const data = await response.json();

        if (!response.ok) {
            liveAvatarStatus.textContent = "Error creando session token.";
            console.error("LiveAvatar token error:", data);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        const sessionId = data?.data?.session_id;
        const sessionToken = data?.data?.session_token;

        if (!sessionId || !sessionToken) {
            liveAvatarStatus.textContent = "LiveAvatar respondió, pero faltan session_id o session_token.";
            console.error("LiveAvatar session data:", data);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        liveAvatarStatus.textContent = "Session token recibido. Cargando SDK de LiveAvatar...";

        const sdkModule = await import("https://esm.sh/@heygen/liveavatar-web-sdk@latest");

        console.log("LiveAvatar SDK module:", sdkModule);

        const LiveAvatarSDK =
            sdkModule.default ||
            sdkModule.LiveAvatar ||
            sdkModule.LiveAvatarClient ||
            sdkModule.LiveAvatarSession;

        if (!LiveAvatarSDK) {
            liveAvatarStatus.textContent = "SDK cargado, pero no encontré la clase principal. Mira la consola.";
            console.error("No compatible SDK export found:", sdkModule);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        liveAvatarStatus.textContent = "SDK cargado. Intentando iniciar sesión de video...";

        liveAvatar = new LiveAvatarSDK({
            sessionToken: sessionToken
        });

        if (typeof liveAvatar.on === "function") {
            liveAvatar.on("stream-ready", function (stream) {
                liveAvatarVideo.srcObject = stream;
                liveAvatarVideo.style.display = "block";
                liveAvatarPlaceholder.style.display = "none";
                liveAvatarStatus.textContent = "LiveAvatar conectado.";
            });

            liveAvatar.on("streamReady", function (stream) {
                liveAvatarVideo.srcObject = stream;
                liveAvatarVideo.style.display = "block";
                liveAvatarPlaceholder.style.display = "none";
                liveAvatarStatus.textContent = "LiveAvatar conectado.";
            });
        }

        if (typeof liveAvatar.start === "function") {
            await liveAvatar.start();
            liveAvatarStatus.textContent = "LiveAvatar iniciado. Esperando stream de video...";
            return;
        }

        if (typeof liveAvatar.connect === "function") {
            await liveAvatar.connect();
            liveAvatarStatus.textContent = "LiveAvatar conectado. Esperando stream de video...";
            return;
        }

        liveAvatarStatus.textContent = "SDK cargado, pero no encontré método start/connect. Mira la consola.";
        console.error("LiveAvatar instance:", liveAvatar);

    } catch (error) {
        liveAvatarStatus.textContent = "Error iniciando LiveAvatar. Mira la consola.";
        console.error(error);
        startLiveAvatarBtn.disabled = false;
    }
}

if (startLiveAvatarBtn) {
    startLiveAvatarBtn.addEventListener("click", startLiveAvatarTest);
}