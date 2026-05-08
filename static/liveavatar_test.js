const startLiveAvatarBtn = document.getElementById("startLiveAvatarBtn");
const liveAvatarStatus = document.getElementById("liveAvatarStatus");
const liveAvatarVideo = document.getElementById("liveAvatarVideo");
const liveAvatarPlaceholder = document.getElementById("liveAvatarPlaceholder");

let liveAvatarSession = null;

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

        const sessionToken = data?.data?.session_token;

        if (!sessionToken) {
            liveAvatarStatus.textContent = "LiveAvatar respondió, pero falta session_token.";
            console.error("LiveAvatar session data:", data);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        liveAvatarStatus.textContent = "Session token recibido. Cargando SDK...";

        const sdkModule = await import("https://esm.sh/@heygen/liveavatar-web-sdk@latest");

        console.log("LiveAvatar SDK module:", sdkModule);

        const {
            LiveAvatarSession,
            SessionEvent,
            ConnectionQuality
        } = sdkModule;

        if (!LiveAvatarSession) {
            liveAvatarStatus.textContent = "No encontré LiveAvatarSession en el SDK.";
            console.error("SDK exports:", sdkModule);
            startLiveAvatarBtn.disabled = false;
            return;
        }

        liveAvatarStatus.textContent = "SDK cargado. Creando sesión...";

        liveAvatarSession = new LiveAvatarSession(sessionToken, {
            apiUrl: "https://api.liveavatar.com",
            voiceChat: false
        });

        // Debug importante: dejamos la sesión accesible desde la consola
        window.liveAvatarSession = liveAvatarSession;

        console.log("LiveAvatar session instance:", liveAvatarSession);
        console.log(
            "LiveAvatar session prototype methods:",
            Object.getOwnPropertyNames(Object.getPrototypeOf(liveAvatarSession))
        );

        console.log(
            "LiveAvatar session own properties:",
            Object.keys(liveAvatarSession)
        );

        if (SessionEvent) {
            console.log("LiveAvatar SessionEvent:", SessionEvent);

            liveAvatarSession.on(SessionEvent.SESSION_STATE_CHANGED, function (state) {
                console.log("LiveAvatar state:", state);
                liveAvatarStatus.textContent = "Estado LiveAvatar: " + state;
            });

            liveAvatarSession.on(SessionEvent.SESSION_STREAM_READY, function () {
                console.log("LiveAvatar stream ready");

                liveAvatarSession.attach(liveAvatarVideo);

                liveAvatarVideo.style.display = "block";
                liveAvatarPlaceholder.style.display = "none";

                liveAvatarStatus.textContent = "LiveAvatar conectado.";
            });

            liveAvatarSession.on(
                SessionEvent.SESSION_CONNECTION_QUALITY_CHANGED,
                function (quality) {
                    console.log("Connection quality:", quality);

                    if (ConnectionQuality && quality === ConnectionQuality.POOR) {
                        liveAvatarStatus.textContent = "LiveAvatar conectado, pero la conexión es débil.";
                    }
                }
            );
        }

        liveAvatarStatus.textContent = "Iniciando LiveAvatar...";

        await liveAvatarSession.start();

        liveAvatarStatus.textContent = "LiveAvatar iniciado. Esperando video...";

        // Debug después de iniciar
        console.log("LiveAvatar session after start:", liveAvatarSession);
        console.log(
            "LiveAvatar methods after start:",
            Object.getOwnPropertyNames(Object.getPrototypeOf(liveAvatarSession))
        );

    } catch (error) {
        liveAvatarStatus.textContent = "Error iniciando LiveAvatar. Mira la consola.";
        console.error(error);
        startLiveAvatarBtn.disabled = false;
    }
}

if (startLiveAvatarBtn) {
    startLiveAvatarBtn.addEventListener("click", startLiveAvatarTest);
}