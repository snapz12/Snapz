/* =========================================================
   SNAPZ POST + REEL MUSIC SYSTEM
   =========================================================
   STORY MUSIC IS NOT USED HERE.
   STORY MUSIC FUNCTIONS / PANEL ARE NOT TOUCHED.

   POST:
   - Maximum 30 seconds
   - Independent trim

   REEL:
   - Uses actual Reel duration
   - Reel preview on trim screen
   - Music duration follows Reel duration
   ========================================================= */

(function () {

    "use strict";

    let currentTarget = null;
    let musicList = [];
    let selectedMusic = null;

    let musicAudio = null;
    let reelVideo = null;

    let musicDuration = 0;
    let trimStart = 0;
    let trimEnd = 0;

    const POST_MAX_DURATION = 30;

    /* =====================================================
       OPEN MUSIC LIBRARY
    ===================================================== */

    window.openSnapzPostReelMusic = function (target) {

        if (target !== "post" && target !== "reel") {
            console.error(
                "SNAPZ MUSIC: invalid target",
                target
            );
            return;
        }

        currentTarget = target;
        selectedMusic = null;

        createLibraryPanel();

        const panel =
            document.getElementById(
                "snapzPostReelMusicPanel"
            );

        if (!panel) {
            return;
        }

        panel.style.display = "block";

        document.body.style.overflow = "hidden";

        const title =
            document.getElementById(
                "snapzPostReelMusicTitle"
            );

        if (title) {
            title.textContent =
                target === "post"
                    ? "Add audio"
                    : "Add audio";
        }

        loadMusic();

    };


    /* =====================================================
       CREATE MUSIC LIBRARY
    ===================================================== */

    function createLibraryPanel() {

        if (
            document.getElementById(
                "snapzPostReelMusicPanel"
            )
        ) {
            return;
        }

        const panel =
            document.createElement("div");

        panel.id =
            "snapzPostReelMusicPanel";

        panel.style.cssText = `
            display:none;
            position:fixed;
            inset:0;
            z-index:1000000000;
            background:#050505;
            color:#fff;
            font-family:Arial,sans-serif;
            overflow-y:auto;
        `;

        panel.innerHTML = `

            <div style="
                position:sticky;
                top:0;
                z-index:10;
                height:64px;
                display:flex;
                align-items:center;
                justify-content:space-between;
                padding:0 18px;
                background:#050505;
                border-bottom:1px solid #242424;
            ">

                <button
                    type="button"
                    id="snapzPostReelMusicBack"
                    style="
                        background:none;
                        border:0;
                        color:#fff;
                        font-size:32px;
                        cursor:pointer;
                    "
                >‹</button>

                <b
                    id="snapzPostReelMusicTitle"
                    style="
                        font-size:19px;
                    "
                >
                    Add audio
                </b>

                <div style="width:32px;"></div>

            </div>

            <div style="
                padding:14px 18px;
            ">

                <input
                    id="snapzPostReelMusicSearch"
                    type="search"
                    placeholder="Search music..."
                    autocomplete="off"
                    style="
                        width:100%;
                        box-sizing:border-box;
                        border:0;
                        outline:none;
                        border-radius:12px;
                        background:#1d1d1d;
                        color:#fff;
                        padding:13px 15px;
                        font-size:16px;
                    "
                >

            </div>

            <div
                id="snapzPostReelMusicList"
                style="
                    padding:0 18px 30px;
                "
            >
                <div style="
                    text-align:center;
                    color:#777;
                    padding:40px;
                ">
                    Loading music...
                </div>
            </div>
        `;

        document.body.appendChild(panel);


        document
            .getElementById(
                "snapzPostReelMusicBack"
            )
            .addEventListener(
                "click",
                closeLibrary
            );


        document
            .getElementById(
                "snapzPostReelMusicSearch"
            )
            .addEventListener(
                "input",
                function () {

                    loadMusic(
                        this.value.trim()
                    );

                }
            );

    }


    /* =====================================================
       CLOSE LIBRARY
    ===================================================== */

    function closeLibrary() {

        stopAudio();

        const panel =
            document.getElementById(
                "snapzPostReelMusicPanel"
            );

        if (panel) {
            panel.style.display = "none";
        }

        document.body.style.overflow = "";

    }


    /* =====================================================
       LOAD MUSIC
    ===================================================== */

    function loadMusic(search = "") {

        const list =
            document.getElementById(
                "snapzPostReelMusicList"
            );

        if (!list) {
            return;
        }

        list.innerHTML = `
            <div style="
                text-align:center;
                color:#777;
                padding:40px;
            ">
                Loading music...
            </div>
        `;

        let url =
            "/music_library";

        if (search) {
            url +=
                "?search=" +
                encodeURIComponent(search);
        }

        fetch(
            url,
            {
                method:"GET",
                credentials:"include",
                headers:{
                    "Accept":
                        "application/json"
                }
            }
        )
        .then(function (response) {

            if (!response.ok) {
                throw new Error(
                    "HTTP " +
                    response.status
                );
            }

            return response.json();

        })
        .then(function (data) {

            if (!Array.isArray(data)) {
                throw new Error(
                    "Invalid music response"
                );
            }

            musicList = data;

            renderMusic();

        })
        .catch(function (error) {

            console.error(
                "POST/REEL MUSIC ERROR:",
                error
            );

            list.innerHTML = `
                <div style="
                    text-align:center;
                    color:#ff6b6b;
                    padding:40px;
                ">
                    Music load failed
                </div>
            `;

        });

    }


    /* =====================================================
       RENDER MUSIC
    ===================================================== */

    function renderMusic() {

        const list =
            document.getElementById(
                "snapzPostReelMusicList"
            );

        if (!list) {
            return;
        }

        if (!musicList.length) {

            list.innerHTML = `
                <div style="
                    text-align:center;
                    color:#777;
                    padding:40px;
                ">
                    No music found
                </div>
            `;

            return;
        }

        list.innerHTML = "";

        musicList.forEach(
            function (music) {

                const row =
                    document.createElement(
                        "div"
                    );

                row.style.cssText = `
                    display:flex;
                    align-items:center;
                    gap:12px;
                    padding:14px 0;
                    border-bottom:1px solid #222;
                `;


                const cover =
                    document.createElement(
                        "div"
                    );

                cover.style.cssText = `
                    width:52px;
                    height:52px;
                    flex-shrink:0;
                    border-radius:10px;
                    overflow:hidden;
                    background:linear-gradient(
                        135deg,
                        #833AB4,
                        #E1306C,
                        #F77737
                    );
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    font-size:25px;
                `;


                if (music.cover_url) {

                    const img =
                        document.createElement(
                            "img"
                        );

                    img.src =
                        music.cover_url;

                    img.style.cssText = `
                        width:100%;
                        height:100%;
                        object-fit:cover;
                    `;

                    img.onerror =
                        function () {
                            this.remove();
                        };

                    cover.appendChild(img);

                } else {

                    cover.textContent = "♪";

                }


                const info =
                    document.createElement(
                        "div"
                    );

                info.style.cssText = `
                    flex:1;
                    min-width:0;
                `;


                const title =
                    document.createElement(
                        "div"
                    );

                title.textContent =
                    music.title ||
                    "Unknown";

                title.style.cssText = `
                    font-size:16px;
                    font-weight:700;
                    white-space:nowrap;
                    overflow:hidden;
                    text-overflow:ellipsis;
                `;


                const by =
                    document.createElement(
                        "div"
                    );

                by.textContent =
                    music.uploaded_by ||
                    "";

                by.style.cssText = `
                    margin-top:4px;
                    color:#777;
                    font-size:12px;
                `;


                const button =
                    document.createElement(
                        "button"
                    );

                button.type =
                    "button";

                button.textContent =
                    "Use";

                button.style.cssText = `
                    border:0;
                    border-radius:20px;
                    padding:9px 16px;
                    background:#0095f6;
                    color:#fff;
                    font-weight:700;
                    cursor:pointer;
                `;


                button.addEventListener(
                    "click",
                    function () {

                        chooseMusic(
                            music
                        );

                    }
                );


                info.appendChild(title);
                info.appendChild(by);

                row.appendChild(cover);
                row.appendChild(info);
                row.appendChild(button);

                list.appendChild(row);

            }
        );

    }


    /* =====================================================
       CHOOSE MUSIC
    ===================================================== */

    function chooseMusic(music) {

        if (
            !music ||
            !music.audio_url
        ) {

            alert(
                "Music URL nahi mila."
            );

            return;
        }

        selectedMusic = {
            id:
                music.id,

            title:
                music.title || "",

            url:
                music.audio_url,

            cover:
                music.cover_url || ""
        };


        prepareTrimScreen();

    }


    /* =====================================================
       PREPARE TRIM SCREEN
    ===================================================== */

    function prepareTrimScreen() {

        stopAudio();

        if (currentTarget === "reel") {

            prepareReelTrim();

        } else {

            preparePostTrim();

        }

    }


    




    /* =====================================================
       RESTORE POST MUSIC
    ===================================================== */

    window.getSnapzPostMusic =
        function () {

            try {

                const data =
                    sessionStorage.getItem(
                        "snapz_post_music"
                    );

                return data
                    ? JSON.parse(data)
                    : null;

            } catch (e) {

                return null;

            }

        };


    /* =====================================================
       RESTORE REEL MUSIC
    ===================================================== */

    window.getSnapzReelMusic =
        function () {

            try {

                const data =
                    sessionStorage.getItem(
                        "snapz_reel_music"
                    );

                return data
                    ? JSON.parse(data)
                    : null;

            } catch (e) {

                return null;

            }

        };


    console.log(
        "SNAPZ POST + REEL MUSIC SYSTEM READY"
    );

})();

/* =========================================================
   SNAPZ NEW INSTAGRAM STYLE MUSIC TRIM
   FRESH SYSTEM
========================================================= */

(function () {

    let snapzNewTrimDragging = null;
    let snapzNewTrimPointerStart = 0;
    let snapzNewTrimStartAtPointer = 0;

    function snapzTrimFullDuration() {

        return (
            Number.isFinite(musicDuration) &&
            musicDuration > 0
        )
            ? musicDuration
            : 30;
    }


    function snapzTrimMaximum() {

        const full = snapzTrimFullDuration();

        if (currentTarget === "post") {

            return Math.min(
                30,
                full
            );

        }

        return Math.min(
            getCurrentReelDuration(),
            full
        );
    }


    /* =====================================================
       CREATE SCREEN
    ===================================================== */

    function createTrimScreen() {

        const old =
            document.getElementById(
                "snapzPostReelTrimPanel"
            );

        if (old) {
            old.remove();
        }

        const panel =
            document.createElement("div");

        panel.id =
            "snapzPostReelTrimPanel";

        panel.style.cssText = `
            position:fixed;
            inset:0;
            z-index:2147483647;
            background:#000;
            color:#fff;
            font-family:Arial,sans-serif;
            overflow:hidden;
            display:flex;
            flex-direction:column;
        `;


        panel.innerHTML = `

            <div style="
                height:60px;
                min-height:60px;
                display:flex;
                align-items:center;
                justify-content:space-between;
                padding:0 16px;
                box-sizing:border-box;
            ">

                <button
                    id="snapzTrimBack"
                    type="button"
                    style="
                        width:42px;
                        height:42px;
                        border:0;
                        background:none;
                        color:#fff;
                        font-size:34px;
                        line-height:1;
                        padding:0;
                    "
                >‹</button>


                <div
                    id="snapzTrimTitle"
                    style="
                        font-size:17px;
                        font-weight:700;
                    "
                >
                    Trim audio
                </div>


                <button
                    id="snapzTrimDone"
                    type="button"
                    style="
                        border:0;
                        background:none;
                        color:#0095f6;
                        font-size:16px;
                        font-weight:700;
                        padding:8px;
                    "
                >
                    Done
                </button>

            </div>


            <div
                id="snapzTrimPreview"
                style="
                    flex:1;
                    min-height:0;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    overflow:hidden;
                    background:#000;
                "
            ></div>


            <div style="
                padding:14px 14px 26px;
                box-sizing:border-box;
                background:#000;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:12px;
                ">

                    <button
                        id="snapzTrimPlay"
                        type="button"
                        style="
                            width:42px;
                            height:42px;
                            border-radius:50%;
                            border:1px solid #555;
                            background:#111;
                            color:#fff;
                            font-size:18px;
                        "
                    >
                        ▶
                    </button>


                    <div style="
                        display:flex;
                        align-items:center;
                        gap:7px;
                        font-size:13px;
                        color:#bbb;
                    ">

                        <span id="snapzTrimStartText">
                            0:00
                        </span>

                        <span>—</span>

                        <span id="snapzTrimEndText">
                            0:30
                        </span>

                    </div>

                </div>


                <div
                    id="snapzMusicTimeline"
                    style="
                        position:relative;
                        width:100%;
                        height:72px;
                        user-select:none;
                        touch-action:none;
                        overflow:visible;
                    "
                >

                    <div style="
                        position:absolute;
                        left:0;
                        right:0;
                        top:0;
                        bottom:0;
                        border-radius:4px;
                        background:#151515;
                    "></div>


                    <div
                        id="snapzTrimOutsideLeft"
                        style="
                            position:absolute;
                            left:0;
                            top:0;
                            bottom:0;
                            background:rgba(0,0,0,.72);
                            pointer-events:none;
                            z-index:3;
                        "
                    ></div>


                    <div
                        id="snapzTrimOutsideRight"
                        style="
                            position:absolute;
                            right:0;
                            top:0;
                            bottom:0;
                            background:rgba(0,0,0,.72);
                            pointer-events:none;
                            z-index:3;
                        "
                    ></div>


                    <div
                        id="snapzTrimSelectedArea"
                        style="
                            position:absolute;
                            top:0;
                            height:100%;
                            box-sizing:border-box;
                            border-top:3px solid #fff;
                            border-bottom:3px solid #fff;
                            z-index:5;
                            touch-action:none;
                        "
                    ></div>


                    <div
                        id="snapzTrimStartHandle"
                        style="
                            position:absolute;
                            top:-4px;
                            bottom:-4px;
                            width:4px;
                            margin-left:-2px;
                            background:#fff;
                            border-radius:3px;
                            z-index:10;
                            touch-action:none;
                        "
                    >
                        <div style="
                            position:absolute;
                            left:-5px;
                            top:0;
                            width:14px;
                            height:18px;
                            background:#fff;
                            border-radius:3px;
                        "></div>
                    </div>


                    <div
                        id="snapzTrimEndHandle"
                        style="
                            position:absolute;
                            top:-4px;
                            bottom:-4px;
                            width:4px;
                            margin-left:-2px;
                            background:#fff;
                            border-radius:3px;
                            z-index:10;
                            touch-action:none;
                        "
                    >
                        <div style="
                            position:absolute;
                            left:-5px;
                            top:0;
                            width:14px;
                            height:18px;
                            background:#fff;
                            border-radius:3px;
                        "></div>
                    </div>


                    <div
                        id="snapzTrimPlayhead"
                        style="
                            position:absolute;
                            top:-6px;
                            bottom:-6px;
                            width:2px;
                            margin-left:-1px;
                            background:#fff;
                            z-index:12;
                            pointer-events:none;
                            display:none;
                        "
                    ></div>

                </div>

            </div>
        `;


        document.body.appendChild(panel);


        const back =
            document.getElementById(
                "snapzTrimBack"
            );

        if (back) {

            back.onclick =
                function () {

                    stopAudio();

                    panel.remove();

                };

        }


        const done =
            document.getElementById(
                "snapzTrimDone"
            );

        if (done) {

            done.onclick =
                function () {

                    finishTrim();

                };

        }


        const play =
            document.getElementById(
                "snapzTrimPlay"
            );

        if (play) {

            play.onclick =
                function () {

                    playTrimPreview();

                };

        }


        setupInstagramTrimControls();

    }


    /* =====================================================
       POST
    ===================================================== */

    function preparePostTrim() {

        currentTarget = "post";

        musicDuration = 0;

        createTrimScreen();


        const title =
            document.getElementById(
                "snapzTrimTitle"
            );

        if (title) {

            title.textContent =
                "Trim audio";

        }


        const preview =
            document.getElementById(
                "snapzTrimPreview"
            );

        if (preview) {

            preview.innerHTML = "";

            const file =
                selectedFiles &&
                selectedFiles.length
                    ? selectedFiles[0]
                    : selectedFile;


            if (
                file &&
                file.type &&
                file.type.startsWith("video/")
            ) {

                const video =
                    document.createElement("video");

                video.src =
                    URL.createObjectURL(file);

                video.playsInline = true;
                video.muted = true;
                video.loop = true;

                video.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:3/4;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(video);

                window.snapzTrimPreviewVideo =
                    video;

                video.play().catch(
                    function () {}
                );

            }

            else if (file) {

                const img =
                    document.createElement("img");

                img.src =
                    URL.createObjectURL(file);

                img.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:3/4;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(img);

            }

        }


        loadMusicMetadata(
            function (duration) {

                musicDuration =
                    Number(duration) || 30;

                const allowed =
                    Math.min(
                        30,
                        musicDuration
                    );

                trimStart = 0;
                trimEnd = allowed;

                setupTrim(allowed);

            }
        );

    }


    /* =====================================================
       REEL
    ===================================================== */

    function prepareReelTrim() {

        currentTarget = "reel";

        createTrimScreen();


        const title =
            document.getElementById(
                "snapzTrimTitle"
            );

        if (title) {

            title.textContent =
                "Trim audio";

        }


        reelVideo =
            document.getElementById(
                "reelEditorVideo"
            );


        let reelDuration = 0;


        if (
            reelVideo &&
            Number.isFinite(
                reelVideo.duration
            ) &&
            reelVideo.duration > 0
        ) {

            reelDuration =
                reelVideo.duration;

        }


        function continueSetup() {

            if (
                !reelDuration &&
                reelVideo
            ) {

                reelDuration =
                    Number(reelVideo.duration) || 0;

            }


            if (!reelDuration) {

                alert(
                    "Reel ki duration detect nahi hui."
                );

                return;

            }


            const preview =
                document.getElementById(
                    "snapzTrimPreview"
                );


            if (preview) {

                preview.innerHTML = "";

                const video =
                    document.createElement("video");

                video.src =
                    reelVideo.currentSrc ||
                    reelVideo.src;

                video.playsInline = true;
                video.muted = true;
                video.loop = true;

                video.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:9/16;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(video);

                window.snapzTrimPreviewVideo =
                    video;

                video.play().catch(
                    function () {}
                );

            }


            loadMusicMetadata(
                function (duration) {

                    musicDuration =
                        Number(duration) || 30;

                    const allowed =
                        Math.min(
                            reelDuration,
                            musicDuration
                        );

                    trimStart = 0;
                    trimEnd = allowed;

                    setupTrim(allowed);

                }
            );

        }


        if (
            reelVideo &&
            Number.isFinite(
                reelVideo.duration
            ) &&
            reelVideo.duration > 0
        ) {

            continueSetup();

        }

        else if (reelVideo) {

            reelVideo.addEventListener(
                "loadedmetadata",
                continueSetup,
                { once:true }
            );

        }

        else {

            alert(
                "Reel preview nahi mila."
            );

        }

    }


    /* =====================================================
       METADATA
    ===================================================== */

    function loadMusicMetadata(callback) {

        if (
            !selectedMusic ||
            !selectedMusic.url
        ) {

            callback(30);

            return;

        }


        const audio =
            new Audio(
                selectedMusic.url
            );

        audio.preload =
            "metadata";


        let done = false;


        function finish(duration) {

            if (done) {
                return;
            }

            done = true;

            callback(
                Number.isFinite(duration) &&
                duration > 0
                    ? duration
                    : 30
            );

        }


        audio.addEventListener(
            "loadedmetadata",
            function () {

                finish(
                    audio.duration
                );

            },
            { once:true }
        );


        audio.addEventListener(
            "error",
            function () {

                console.error(
                    "SNAPZ music metadata error"
                );

                finish(30);

            },
            { once:true }
        );


        try {

            audio.load();

        } catch (e) {

            finish(30);

        }

    }


    /* =====================================================
       SETUP
    ===================================================== */

    function setupTrim(allowedDuration) {

        const full =
            snapzTrimFullDuration();

        const max =
            Math.min(
                allowedDuration,
                full
            );


        trimStart = 0;

        trimEnd = max;


        updateInstagramTrimUI();

        updateTrimText();

    }


    /* =====================================================
       UI
    ===================================================== */

    function updateInstagramTrimUI() {

        const timeline =
            document.getElementById(
                "snapzMusicTimeline"
            );

        const selected =
            document.getElementById(
                "snapzTrimSelectedArea"
            );

        const left =
            document.getElementById(
                "snapzTrimOutsideLeft"
            );

        const right =
            document.getElementById(
                "snapzTrimOutsideRight"
            );

        const startHandle =
            document.getElementById(
                "snapzTrimStartHandle"
            );

        const endHandle =
            document.getElementById(
                "snapzTrimEndHandle"
            );


        if (
            !timeline ||
            !musicDuration
        ) {

            return;

        }


        const full =
            musicDuration;


        const startPercent =
            Math.max(
                0,
                Math.min(
                    100,
                    (trimStart / full) * 100
                )
            );


        const endPercent =
            Math.max(
                0,
                Math.min(
                    100,
                    (trimEnd / full) * 100
                )
            );


        const width =
            Math.max(
                0,
                endPercent - startPercent
            );


        if (selected) {

            selected.style.left =
                startPercent + "%";

            selected.style.width =
                width + "%";

        }


        if (left) {

            left.style.width =
                startPercent + "%";

        }


        if (right) {

            right.style.width =
                (100 - endPercent) + "%";

        }


        if (startHandle) {

            startHandle.style.left =
                startPercent + "%";

        }


        if (endHandle) {

            endHandle.style.left =
                endPercent + "%";

        }


        createSnapzNewWaveform();

        updateTrimText();

    }


    /* =====================================================
       WAVEFORM
    ===================================================== */

    function createSnapzNewWaveform() {

        const timeline =
            document.getElementById(
                "snapzMusicTimeline"
            );

        if (!timeline) {
            return;
        }


        const old =
            timeline.querySelector(
                ".snapzNewWaveform"
            );

        if (old) {
            old.remove();
        }


        const waveform =
            document.createElement("div");

        waveform.className =
            "snapzNewWaveform";


        waveform.style.cssText = `
            position:absolute;
            inset:0;
            display:flex;
            align-items:center;
            justify-content:space-between;
            gap:2px;
            padding:8px 5px;
            box-sizing:border-box;
            pointer-events:none;
            z-index:1;
            overflow:hidden;
            border-radius:4px;
        `;


        const bars = 100;


        for (
            let i = 0;
            i < bars;
            i++
        ) {

            const bar =
                document.createElement("div");


            const wave =
                Math.abs(
                    Math.sin(
                        (i + 1) * 1.71
                    )
                );


            const height =
                8 +
                Math.round(
                    wave * 45
                );


            bar.style.cssText = `
                flex:1;
                min-width:1px;
                max-width:5px;
                height:${height}px;
                border-radius:2px;
                background:#777;
            `;


            waveform.appendChild(bar);

        }


        timeline.insertBefore(
            waveform,
            timeline.firstChild
        );

    }


    /* =====================================================
       TEXT
    ===================================================== */

    function updateTrimText() {

        const a =
            document.getElementById(
                "snapzTrimStartText"
            );

        const b =
            document.getElementById(
                "snapzTrimEndText"
            );


        if (a) {

            a.textContent =
                formatTime(
                    trimStart
                );

        }


        if (b) {

            b.textContent =
                formatTime(
                    trimEnd
                );

        }

    }


    function formatTime(seconds) {

        seconds =
            Math.max(
                0,
                Number(seconds) || 0
            );


        const minutes =
            Math.floor(
                seconds / 60
            );


        const secs =
            Math.floor(
                seconds % 60
            );


        return (
            minutes +
            ":" +
            String(secs).padStart(
                2,
                "0"
            )
        );

    }


    /* =====================================================
       DRAG SYSTEM
    ===================================================== */

    function setupInstagramTrimControls() {

    const timeline =
        document.getElementById("snapzMusicTimeline");

    const selectedArea =
        document.getElementById("snapzTrimSelectedArea");

    const startHandle =
        document.getElementById("snapzTrimStartHandle");

    const endHandle =
        document.getElementById("snapzTrimEndHandle");

    if (!timeline || !selectedArea) {
        return;
    }

    /*
     * SNAPZ INSTAGRAM STYLE
     *
     * LEFT HANDLE  = FIXED
     * RIGHT HANDLE = FIXED
     *
     * ONLY MIDDLE SELECTED WINDOW MOVES.
     */

    let dragging = false;
    let pointerStartX = 0;
    let originalStart = 0;
    let originalEnd = 0;

    function fullDuration() {

        return (
            Number.isFinite(musicDuration) &&
            musicDuration > 0
        )
            ? musicDuration
            : 30;
    }

    function renderTrimWindow() {

        const full = fullDuration();

        if (!full) return;

        const left =
            (trimStart / full) * 100;

        const width =
            ((trimEnd - trimStart) / full) * 100;

        selectedArea.style.left =
            left + "%";

        selectedArea.style.width =
            width + "%";

        /*
         * Handles visually follow the window,
         * but POINTER EVENTS ARE LOCKED.
         */

        if (startHandle) {

            startHandle.style.left =
                left + "%";

            startHandle.style.pointerEvents =
                "none";
        }

        if (endHandle) {

            endHandle.style.left =
                ((trimEnd / full) * 100) + "%";

            endHandle.style.pointerEvents =
                "none";
        }

        const start =
            document.getElementById(
                "snapzTrimStart"
            );

        const end =
            document.getElementById(
                "snapzTrimEnd"
            );

        if (start) {
            start.value = trimStart;
        }

        if (end) {
            end.value = trimEnd;
        }

        updateTrimText();
    }

    function getPointerTime(clientX) {

        const rect =
            timeline.getBoundingClientRect();

        if (!rect.width) {
            return 0;
        }

        let ratio =
            (clientX - rect.left) /
            rect.width;

        ratio =
            Math.max(
                0,
                Math.min(
                    1,
                    ratio
                )
            );

        return ratio * fullDuration();
    }

    function isInsideSelectedWindow(clientX) {

        const t =
            getPointerTime(clientX);

        return (
            t >= trimStart &&
            t <= trimEnd
        );
    }

    function startDrag(e) {

        /*
         * NEVER allow either handle to drag.
         */

        if (
            e.target === startHandle ||
            e.target === endHandle ||
            (
                e.target.closest &&
                (
                    e.target.closest(
                        "#snapzTrimStartHandle"
                    ) ||
                    e.target.closest(
                        "#snapzTrimEndHandle"
                    )
                )
            )
        ) {
            return;
        }

        /*
         * Only the selected middle area.
         */

        if (!isInsideSelectedWindow(e.clientX)) {
            return;
        }

        dragging = true;

        pointerStartX =
            e.clientX;

        originalStart =
            trimStart;

        originalEnd =
            trimEnd;

        try {
            timeline.setPointerCapture(
                e.pointerId
            );
        } catch (_) {}

        e.preventDefault();
        e.stopPropagation();
    }

    function moveDrag(e) {

        if (!dragging) {
            return;
        }

        const full =
            fullDuration();

        const rect =
            timeline.getBoundingClientRect();

        if (!rect.width) {
            return;
        }

        const selectedDuration =
            originalEnd -
            originalStart;

        const delta =
            (
                (e.clientX - pointerStartX) /
                rect.width
            ) * full;

        let newStart =
            originalStart + delta;

        let newEnd =
            originalEnd + delta;

        /*
         * Keep complete selected window
         * inside full song.
         */

        if (newStart < 0) {

            newStart = 0;
            newEnd =
                selectedDuration;
        }

        if (newEnd > full) {

            newEnd = full;
            newStart =
                full -
                selectedDuration;
        }

        trimStart =
            Math.max(
                0,
                newStart
            );

        trimEnd =
            Math.min(
                full,
                newEnd
            );

        renderTrimWindow();

        e.preventDefault();
        e.stopPropagation();
    }

    function endDrag(e) {

        if (!dragging) {
            return;
        }

        dragging = false;

        try {
            timeline.releasePointerCapture(
                e.pointerId
            );
        } catch (_) {}

        renderTrimWindow();

        if (e) {
            e.preventDefault();
            e.stopPropagation();
        }
    }


    /*
     * =====================================================
     * LOCK LEFT + RIGHT HANDLES
     * =====================================================
     */

    if (startHandle) {

        startHandle.style.pointerEvents =
            "none";

        startHandle.onpointerdown =
            null;

        startHandle.onmousedown =
            null;

        startHandle.ontouchstart =
            null;
    }

    if (endHandle) {

        endHandle.style.pointerEvents =
            "none";

        endHandle.onpointerdown =
            null;

        endHandle.onmousedown =
            null;

        endHandle.ontouchstart =
            null;
    }


    /*
     * =====================================================
     * ONLY SELECTED MIDDLE WINDOW DRAGS
     * =====================================================
     */

    timeline.onpointerdown =
        startDrag;

    timeline.onpointermove =
        moveDrag;

    timeline.onpointerup =
        endDrag;

    timeline.onpointercancel =
        endDrag;


    selectedArea.style.pointerEvents =
        "auto";

    selectedArea.style.touchAction =
        "none";

    selectedArea.onpointerdown =
        startDrag;

    selectedArea.onpointermove =
        moveDrag;

    selectedArea.onpointerup =
        endDrag;

    selectedArea.onpointercancel =
        endDrag;


    renderTrimWindow();

    console.log(
        "SNAPZ TRIM: LEFT HANDLE LOCKED"
    );

    console.log(
        "SNAPZ TRIM: RIGHT HANDLE LOCKED"
    );

    console.log(
        "SNAPZ TRIM: MIDDLE WINDOW DRAG ONLY"
    );
}



        function percentFromEvent(event) {

            const rect =
                timeline.getBoundingClientRect();

            let x =
                event.clientX -
                rect.left;


            x =
                Math.max(
                    0,
                    Math.min(
                        rect.width,
                        x
                    )
                );


            return (
                x / rect.width
            );

        }


        function beginDrag(type, event) {

            event.preventDefault();
            event.stopPropagation();

            snapzNewTrimDragging =
                type;

            snapzNewTrimPointerStart =
                event.clientX;

            snapzNewTrimStartAtPointer =
                trimStart;


            try {

                event.currentTarget.setPointerCapture(
                    event.pointerId
                );

            } catch (e) {}

        }


        function moveDrag(event) {

            if (!snapzNewTrimDragging) {
                return;
            }


            event.preventDefault();


            const full =
                snapzTrimFullDuration();

            const max =
                snapzTrimMaximum();


            if (
                snapzNewTrimDragging ===
                "start"
            ) {

                let s =
                    percentFromEvent(event) *
                    full;


                s =
                    Math.max(
                        0,
                        Math.min(
                            s,
                            trimEnd - 0.05
                        )
                    );


                if (
                    trimEnd - s >
                    max
                ) {

                    s =
                        trimEnd -
                        max;

                }


                trimStart =
                    Math.max(
                        0,
                        s
                    );

            }


            else if (
                snapzNewTrimDragging ===
                "end"
            ) {

                let e =
                    percentFromEvent(event) *
                    full;


                e =
                    Math.max(
                        trimStart + 0.05,
                        Math.min(
                            e,
                            full
                        )
                    );


                if (
                    e - trimStart >
                    max
                ) {

                    e =
                        trimStart +
                        max;

                }


                trimEnd =
                    Math.min(
                        full,
                        e
                    );

            }


            else if (
                snapzNewTrimDragging ===
                "middle"
            ) {

                const rect =
                    timeline.getBoundingClientRect();


                const delta =
                    (
                        event.clientX -
                        snapzNewTrimPointerStart
                    ) /
                    rect.width *
                    full;


                const length =
                    trimEnd -
                    trimStart;


                let s =
                    snapzNewTrimStartAtPointer +
                    delta;


                s =
                    Math.max(
                        0,
                        Math.min(
                            s,
                            full - length
                        )
                    );


                trimStart =
                    s;

                trimEnd =
                    s +
                    length;

            }


            updateInstagramTrimUI();

        }


        function endDrag(event) {

            if (!snapzNewTrimDragging) {
                return;
            }


            try {

                event.currentTarget.releasePointerCapture(
                    event.pointerId
                );

            } catch (e) {}


            snapzNewTrimDragging =
                null;

        }


        startHandle.addEventListener(
            "pointerdown",
            function (e) {

                beginDrag(
                    "start",
                    e
                );

            }
        );


        endHandle.addEventListener(
            "pointerdown",
            function (e) {

                beginDrag(
                    "end",
                    e
                );

            }
        );


        selected.addEventListener(
            "pointerdown",
            function (e) {

                beginDrag(
                    "middle",
                    e
                );

            }
        );


        timeline.addEventListener(
            "pointermove",
            moveDrag
        );


        timeline.addEventListener(
            "pointerup",
            endDrag
        );


        timeline.addEventListener(
            "pointercancel",
            endDrag
        );


        timeline.addEventListener(
            "pointerleave",
            function () {

                if (
                    snapzNewTrimDragging
                ) {

                    /* keep dragging */

                }

            }
        );

    }


    /* =====================================================
       PLAYHEAD
    ===================================================== */

    function setTrimPlayhead(time) {

        const playhead =
            document.getElementById(
                "snapzTrimPlayhead"
            );

        if (
            !playhead ||
            !musicDuration
        ) {

            return;

        }


        time =
            Math.max(
                trimStart,
                Math.min(
                    trimEnd,
                    Number(time) || trimStart
                )
            );


        playhead.style.left =
            (
                time /
                musicDuration *
                100
            ) + "%";


        playhead.style.display =
            "block";

    }


    /* =====================================================
       FINISH
    ===================================================== */

    function finishTrim() {

        if (!selectedMusic) {
            return;
        }


        const data = {

            id:
                selectedMusic.id,

            title:
                selectedMusic.title,

            url:
                selectedMusic.url,

            cover:
                selectedMusic.cover,

            start:
                Number(
                    trimStart.toFixed(3)
                ),

            end:
                Number(
                    trimEnd.toFixed(3)
                ),

            duration:
                Number(
                    (
                        trimEnd -
                        trimStart
                    ).toFixed(3)
                ),

            target:
                currentTarget

        };


        if (
            currentTarget ===
            "post"
        ) {

            window.snapzPostMusic =
                data;


            sessionStorage.setItem(
                "snapz_post_music",
                JSON.stringify(data)
            );


            if (
                typeof window.refreshSnapzPostMusic ===
                "function"
            ) {

                window.refreshSnapzPostMusic();

            }

        }


        if (
            currentTarget ===
            "reel"
        ) {

            window.snapzReelMusic =
                data;


            sessionStorage.setItem(
                "snapz_reel_music",
                JSON.stringify(data)
            );


            if (
                typeof window.refreshSnapzReelMusic ===
                "function"
            ) {

                window.refreshSnapzReelMusic();

            }

        }


        stopAudio();


        if (
            window.snapzTrimPreviewVideo
        ) {

            try {

                window.snapzTrimPreviewVideo.pause();

            } catch (e) {}


            window.snapzTrimPreviewVideo =
                null;

        }


        const panel =
            document.getElementById(
                "snapzPostReelTrimPanel"
            );

        if (panel) {
            panel.remove();
        }


        if (
            typeof closeLibrary ===
            "function"
        ) {

            closeLibrary();

        }

    }


    /* =====================================================
       PREPARE TRIM SCREEN OVERRIDE
    ===================================================== */

    function prepareTrimScreen() {

        stopAudio();


        if (
            currentTarget ===
            "post"
        ) {

            preparePostTrim();

        }

        else if (
            currentTarget ===
            "reel"
        ) {

            prepareReelTrim();

        }

    }


    /*
     * Expose functions so existing Snapz
     * music-selection code can continue working.
     */

    window.createTrimScreen =
        createTrimScreen;

    window.prepareTrimScreen =
        prepareTrimScreen;

    window.preparePostTrim =
        preparePostTrim;

    window.prepareReelTrim =
        prepareReelTrim;

    window.setupTrim =
        setupTrim;

    window.updateInstagramTrimUI =
        updateInstagramTrimUI;

    window.setupInstagramTrimControls =
        setupInstagramTrimControls;

    window.finishTrim =
        finishTrim;

})();

