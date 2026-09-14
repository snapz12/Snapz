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
       CREATE TRIM SCREEN
    ===================================================== */

    function createTrimScreen() {

        let old =
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
            z-index:1000000001;
            background:#000;
            color:#fff;
            font-family:Arial,sans-serif;
            overflow:hidden;
        `;

        panel.innerHTML = `

            <div style="
                height:64px;
                display:flex;
                align-items:center;
                justify-content:space-between;
                padding:0 18px;
                box-sizing:border-box;
                border-bottom:1px solid #202020;
                background:#000;
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
                        cursor:pointer;
                    "
                >‹</button>

                <div
                    id="snapzTrimTitle"
                    style="
                        font-size:18px;
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
                        cursor:pointer;
                    "
                >
                    Done
                </button>

            </div>


            <!-- PREVIEW -->

            <div
                id="snapzTrimPreview"
                style="
                    height:52%;
                    min-height:260px;
                    display:flex;
                    align-items:center;
                    justify-content:center;
                    background:#000;
                    overflow:hidden;
                    box-sizing:border-box;
                "
            ></div>


            <!-- MUSIC AREA -->

            <div style="
                position:absolute;
                left:0;
                right:0;
                bottom:0;
                background:#000;
                padding:18px 16px 24px;
                box-sizing:border-box;
            ">

                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                    margin-bottom:10px;
                    font-size:13px;
                    color:#aaa;
                ">

                    <span id="snapzTrimStartText">
                        0:00
                    </span>

                    <span
                        id="snapzTrimCurrentText"
                        style="
                            color:#fff;
                            font-weight:700;
                        "
                    >
                        0:00
                    </span>

                    <span id="snapzTrimEndText">
                        0:30
                    </span>

                </div>


                <!-- INSTAGRAM STYLE TIMELINE -->

                <div
                    id="snapzMusicTimeline"
                    style="
                        position:relative;
                        width:100%;
                        height:76px;
                        user-select:none;
                        touch-action:none;
                        box-sizing:border-box;
                    "
                >

                    <div
                        id="snapzMusicWaveform"
                        style="
                            position:absolute;
                            left:0;
                            right:0;
                            top:8px;
                            bottom:8px;
                            display:flex;
                            align-items:center;
                            gap:2px;
                            overflow:hidden;
                            border-radius:8px;
                        "
                    ></div>


                    <!-- DARK OUTSIDE LEFT -->

                    <div
                        id="snapzTrimOutsideLeft"
                        style="
                            position:absolute;
                            top:8px;
                            bottom:8px;
                            left:0;
                            width:0;
                            background:rgba(0,0,0,.72);
                            pointer-events:none;
                            z-index:3;
                        "
                    ></div>


                    <!-- SELECTED AREA -->

                    <div
                        id="snapzTrimSelectedArea"
                        style="
                            position:absolute;
                            top:8px;
                            bottom:8px;
                            left:0;
                            width:100%;
                            border:2px solid #fff;
                            border-radius:5px;
                            box-sizing:border-box;
                            z-index:4;
                            cursor:pointer;
                        "
                    ></div>


                    <!-- DARK OUTSIDE RIGHT -->

                    <div
                        id="snapzTrimOutsideRight"
                        style="
                            position:absolute;
                            top:8px;
                            bottom:8px;
                            right:0;
                            width:0;
                            background:rgba(0,0,0,.72);
                            pointer-events:none;
                            z-index:3;
                        "
                    ></div>


                    <!-- START HANDLE -->

                    <div
                        id="snapzTrimStartHandle"
                        style="
                            position:absolute;
                            top:0;
                            bottom:0;
                            left:0;
                            width:18px;
                            margin-left:-9px;
                            z-index:8;
                            cursor:ew-resize;
                            touch-action:none;
                        "
                    >
                        <div style="
                            position:absolute;
                            left:5px;
                            top:0;
                            bottom:0;
                            width:8px;
                            background:#fff;
                            border-radius:5px;
                        "></div>
                    </div>


                    <!-- END HANDLE -->

                    <div
                        id="snapzTrimEndHandle"
                        style="
                            position:absolute;
                            top:0;
                            bottom:0;
                            right:0;
                            width:18px;
                            margin-right:-9px;
                            z-index:8;
                            cursor:ew-resize;
                            touch-action:none;
                        "
                    >
                        <div style="
                            position:absolute;
                            left:5px;
                            top:0;
                            bottom:0;
                            width:8px;
                            background:#fff;
                            border-radius:5px;
                        "></div>
                    </div>


                    <!-- PLAYHEAD -->

                    <div
                        id="snapzTrimPlayhead"
                        style="
                            position:absolute;
                            top:0;
                            bottom:0;
                            left:0;
                            width:2px;
                            background:#fff;
                            z-index:10;
                            pointer-events:none;
                        "
                    ></div>

                </div>


                <div style="
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    margin-top:10px;
                ">

                    <button
                        id="snapzTrimPlay"
                        type="button"
                        style="
                            width:54px;
                            height:54px;
                            border-radius:50%;
                            border:0;
                            background:#fff;
                            color:#000;
                            font-size:20px;
                            cursor:pointer;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                        "
                    >
                        ▶
                    </button>

                </div>

            </div>
        `;

        document.body.appendChild(panel);


        document
            .getElementById("snapzTrimBack")
            .onclick =
                function () {

                    stopAudio();

                    panel.remove();

                    const library =
                        document.getElementById(
                            "snapzPostReelMusicPanel"
                        );

                    if (library) {
                        library.style.display =
                            "block";
                    }

                };


        document
            .getElementById("snapzTrimDone")
            .onclick =
                function () {

                    finishTrim();

                };


        document
            .getElementById("snapzTrimPlay")
            .onclick =
                function () {

                    playTrimPreview();

                };


        setupInstagramTrimControls();

    }


    /* =====================================================
       INSTAGRAM STYLE TRIM CONTROLS
    ===================================================== */

    

function setupInstagramTrimControls() {

    const timeline =
        document.getElementById(
            "snapzMusicTimeline"
        );

    const selected =
        document.getElementById(
            "snapzTrimSelectedArea"
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
        !selected ||
        !startHandle ||
        !endHandle
    ) {
        return;
    }


    /*
     * REMOVE PREVIOUS POINTER EVENTS
     */

    if (
        timeline.__snapzTrimCleanup
    ) {

        try {
            timeline.__snapzTrimCleanup();
        } catch (e) {}
    }


    let dragging =
        null;

    let pointerStartX =
        0;

    let originalStart =
        0;

    let originalEnd =
        0;


    /*
     * FULL SONG POSITION
     */

    function pointerTime(event) {

        const rect =
            timeline.getBoundingClientRect();


        if (!rect.width) {
            return 0;
        }


        let percent =
            (
                event.clientX -
                rect.left
            ) / rect.width;


        percent =
            Math.max(
                0,
                Math.min(
                    1,
                    percent
                )
            );


        return (
            percent *
            musicDuration
        );
    }


    /*
     * HANDLE DRAG
     */

    function startHandleDrag(
        event
    ) {

        event.preventDefault();
        event.stopPropagation();

        dragging =
            "start";

        if (
            event.currentTarget &&
            event.currentTarget.setPointerCapture &&
            event.pointerId !== undefined
        ) {

            try {
                event.currentTarget
                    .setPointerCapture(
                        event.pointerId
                    );
            } catch (e) {}
        }
    }


    function endHandleDrag(
        event
    ) {

        event.preventDefault();
        event.stopPropagation();

        dragging =
            "end";

        if (
            event.currentTarget &&
            event.currentTarget.setPointerCapture &&
            event.pointerId !== undefined
        ) {

            try {
                event.currentTarget
                    .setPointerCapture(
                        event.pointerId
                    );
            } catch (e) {}
        }
    }


    /*
     * MIDDLE WINDOW DRAG
     */

    function selectedDragStart(
        event
    ) {

        event.preventDefault();
        event.stopPropagation();

        dragging =
            "window";

        pointerStartX =
            event.clientX;

        originalStart =
            trimStart;

        originalEnd =
            trimEnd;


        if (
            selected.setPointerCapture &&
            event.pointerId !== undefined
        ) {

            try {
                selected.setPointerCapture(
                    event.pointerId
                );
            } catch (e) {}
        }
    }


    /*
     * POINTER MOVE
     */

    function pointerMove(
        event
    ) {

        if (!dragging) {
            return;
        }


        const rect =
            timeline.getBoundingClientRect();


        if (!rect.width) {
            return;
        }


        const duration =
            musicDuration;


        /*
         * HANDLE MOVEMENT
         */

        if (
            dragging ===
            "start"
        ) {

            let time =
                pointerTime(event);


            const maxAllowed =
                currentTarget ===
                "post"

                    ? Math.min(
                        POST_MAX_DURATION ||
                            30,
                        duration
                    )

                    : Math.min(
                        Number(
                            getCurrentReelDuration()
                        ) || duration,
                        duration
                    );


            time =
                Math.max(
                    0,
                    Math.min(
                        time,
                        trimEnd - 0.05
                    )
                );


            if (
                trimEnd - time >
                maxAllowed
            ) {

                time =
                    trimEnd -
                    maxAllowed;
            }


            trimStart =
                Math.max(
                    0,
                    time
                );


            const input =
                document.getElementById(
                    "snapzTrimStart"
                );


            if (input) {
                input.value =
                    trimStart;
            }


            updateInstagramTrimUI();

            return;
        }


        /*
         * END HANDLE
         */

        if (
            dragging ===
            "end"
        ) {

            let time =
                pointerTime(event);


            const maxAllowed =
                currentTarget ===
                "post"

                    ? Math.min(
                        POST_MAX_DURATION ||
                            30,
                        duration
                    )

                    : Math.min(
                        Number(
                            getCurrentReelDuration()
                        ) || duration,
                        duration
                    );


            time =
                Math.max(
                    trimStart + 0.05,
                    Math.min(
                        time,
                        duration
                    )
                );


            if (
                time - trimStart >
                maxAllowed
            ) {

                time =
                    trimStart +
                    maxAllowed;
            }


            trimEnd =
                Math.min(
                    duration,
                    time
                );


            const input =
                document.getElementById(
                    "snapzTrimEnd"
                );


            if (input) {
                input.value =
                    trimEnd;
            }


            updateInstagramTrimUI();

            return;
        }


        /*
         * MOVE ENTIRE SELECTED WINDOW
         */

        if (
            dragging ===
            "window"
        ) {

            const deltaPixels =
                event.clientX -
                pointerStartX;


            const deltaTime =
                (
                    deltaPixels /
                    rect.width
                ) * duration;


            const windowLength =
                originalEnd -
                originalStart;


            let newStart =
                originalStart +
                deltaTime;


            let newEnd =
                originalEnd +
                deltaTime;


            /*
             * LEFT EDGE
             */

            if (
                newStart < 0
            ) {

                newStart = 0;

                newEnd =
                    windowLength;
            }


            /*
             * RIGHT EDGE
             */

            if (
                newEnd >
                duration
            ) {

                newEnd =
                    duration;

                newStart =
                    duration -
                    windowLength;
            }


            trimStart =
                Math.max(
                    0,
                    newStart
                );

            trimEnd =
                Math.min(
                    duration,
                    newEnd
                );


            const startInput =
                document.getElementById(
                    "snapzTrimStart"
                );

            const endInput =
                document.getElementById(
                    "snapzTrimEnd"
                );


            if (startInput) {
                startInput.value =
                    trimStart;
            }

            if (endInput) {
                endInput.value =
                    trimEnd;
            }


            updateInstagramTrimUI();
        }
    }


    /*
     * POINTER UP
     */

    function pointerUp(
        event
    ) {

        dragging =
            null;

        try {

            if (
                event.currentTarget &&
                event.currentTarget.releasePointerCapture &&
                event.pointerId !== undefined
            ) {

                event.currentTarget
                    .releasePointerCapture(
                        event.pointerId
                    );
            }

        } catch (e) {}
    }


    /*
     * EVENTS
     */

    startHandle.addEventListener(
        "pointerdown",
        startHandleDrag
    );

    endHandle.addEventListener(
        "pointerdown",
        endHandleDrag
    );


    /*
     * IMPORTANT:
     *
     * ONLY THE SELECTED AREA
     * MOVES THE WHOLE WINDOW.
     *
     * This makes the screenshot-style
     * Instagram trim behavior.
     */

    selected.addEventListener(
        "pointerdown",
        selectedDragStart
    );


    window.addEventListener(
        "pointermove",
        pointerMove
    );


    window.addEventListener(
        "pointerup",
        pointerUp
    );


    window.addEventListener(
        "pointercancel",
        pointerUp
    );


    /*
     * STORE CLEANUP
     */

    timeline.__snapzTrimCleanup =
        function () {

            try {
                startHandle.removeEventListener(
                    "pointerdown",
                    startHandleDrag
                );

                endHandle.removeEventListener(
                    "pointerdown",
                    endHandleDrag
                );

                selected.removeEventListener(
                    "pointerdown",
                    selectedDragStart
                );

                window.removeEventListener(
                    "pointermove",
                    pointerMove
                );

                window.removeEventListener(
                    "pointerup",
                    pointerUp
                );

                window.removeEventListener(
                    "pointercancel",
                    pointerUp
                );

            } catch (e) {}
        };


    /*
     * INITIAL UI
     */

    updateInstagramTrimUI();
}




    /* =====================================================
       WAVEFORM
    ===================================================== */

    

function createInstagramWaveform() {

    const timeline =
        document.getElementById(
            "snapzMusicTimeline"
        );

    if (!timeline) {
        return;
    }

    const duration =
        Number.isFinite(musicDuration) &&
        musicDuration > 0
            ? musicDuration
            : 30;

    /*
     * REMOVE ONLY OLD WAVEFORM
     */

    const old =
        timeline.querySelector(
            ".snapzInstagramWaveform"
        );

    if (old) {
        old.remove();
    }

    /*
     * FULL SONG WAVEFORM
     */

    const waveform =
        document.createElement("div");

    waveform.className =
        "snapzInstagramWaveform";

    waveform.style.cssText = `
        position:absolute;
        left:0;
        right:0;
        top:0;
        bottom:0;

        display:flex;
        align-items:center;
        justify-content:space-between;

        gap:3px;
        padding:0 6px;

        box-sizing:border-box;

        pointer-events:none;

        z-index:1;
        overflow:hidden;
    `;

    const bars = 70;

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
                    (i + 1) * 1.47
                )
            );

        const height =
            12 +
            Math.round(
                wave * 34
            );

        bar.style.cssText = `
            flex:1;
            min-width:2px;
            max-width:6px;

            height:${height}px;

            border-radius:4px;

            background:rgba(150,150,150,.65);
        `;

        waveform.appendChild(bar);
    }

    /*
     * PUT FULL WAVEFORM FIRST
     */

    timeline.insertBefore(
        waveform,
        timeline.firstChild
    );


    /*
     * SELECTED WINDOW
     */

    const selected =
        document.getElementById(
            "snapzTrimSelectedArea"
        );

    const startHandle =
        document.getElementById(
            "snapzTrimStartHandle"
        );

    const endHandle =
        document.getElementById(
            "snapzTrimEndHandle"
        );


    if (selected) {

        selected.style.position =
            "absolute";

        selected.style.top =
            "0";

        selected.style.bottom =
            "0";

        selected.style.zIndex =
            "5";

        selected.style.boxSizing =
            "border-box";

        selected.style.overflow =
            "hidden";

        selected.style.pointerEvents =
            "auto";
    }


    /*
     * INITIAL POSITION
     */

    const left =
        (trimStart / duration) *
        100;

    const width =
        ((trimEnd - trimStart) /
            duration) * 100;


    if (selected) {

        selected.style.left =
            left + "%";

        selected.style.width =
            width + "%";
    }


    if (startHandle) {

        startHandle.style.position =
            "absolute";

        startHandle.style.left =
            left + "%";

        startHandle.style.zIndex =
            "20";
    }


    if (endHandle) {

        endHandle.style.position =
            "absolute";

        endHandle.style.left =
            ((trimEnd / duration) *
                100) + "%";

        endHandle.style.right =
            "auto";

        endHandle.style.zIndex =
            "20";
    }


    /*
     * STORE FULL SONG DURATION
     */

    timeline.dataset.fullDuration =
        String(duration);
}




    /* =====================================================
       TRIM UI
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

    const leftOutside =
        document.getElementById(
            "snapzTrimOutsideLeft"
        );

    const rightOutside =
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


    const duration =
        musicDuration;


    let s =
        Number(trimStart);

    let e =
        Number(trimEnd);


    if (!Number.isFinite(s)) {
        s = 0;
    }

    if (!Number.isFinite(e)) {
        e = duration;
    }


    s =
        Math.max(
            0,
            Math.min(
                duration,
                s
            )
        );

    e =
        Math.max(
            0,
            Math.min(
                duration,
                e
            )
        );


    /*
     * KEEP VALID WINDOW
     */

    if (e <= s) {

        e =
            Math.min(
                duration,
                s + 0.1
            );
    }


    trimStart = s;
    trimEnd = e;


    const startPercent =
        (s / duration) * 100;

    const endPercent =
        (e / duration) * 100;

    const widthPercent =
        ((e - s) /
            duration) * 100;


    /*
     * SELECTED WINDOW
     */

    if (selected) {

        selected.style.left =
            startPercent + "%";

        selected.style.width =
            widthPercent + "%";

        selected.style.zIndex =
            "5";
    }


    /*
     * OUTSIDE AREAS
     */

    if (leftOutside) {

        leftOutside.style.width =
            startPercent + "%";
    }


    if (rightOutside) {

        rightOutside.style.width =
            (100 - endPercent) + "%";
    }


    /*
     * START HANDLE
     */

    if (startHandle) {

        startHandle.style.left =
            startPercent + "%";

        startHandle.style.right =
            "auto";

        startHandle.style.zIndex =
            "30";
    }


    /*
     * END HANDLE
     */

    if (endHandle) {

        endHandle.style.left =
            endPercent + "%";

        endHandle.style.right =
            "auto";

        endHandle.style.zIndex =
            "30";
    }


    updateTrimText();
}



    /* =====================================================
       PLAYHEAD
    ===================================================== */

    function setTrimPlayhead(time) {

        if (!musicDuration) {
            return;
        }

        time =
            Math.max(
                trimStart,
                Math.min(
                    trimEnd,
                    time
                )
            );


        const playhead =
            document.getElementById(
                "snapzTrimPlayhead"
            );

        if (playhead) {

            playhead.style.left =
                (
                    time /
                    musicDuration *
                    100
                ) + "%";

        }


        const current =
            document.getElementById(
                "snapzTrimCurrentText"
            );

        if (current) {

            current.textContent =
                formatTime(
                    time
                );

        }


        if (musicAudio) {

            try {

                musicAudio.currentTime =
                    time;

            } catch (e) {}

        }

        if (window.snapzTrimPreviewVideo) {

            try {

                window.snapzTrimPreviewVideo.currentTime =
                    time;

            } catch (e) {}

        }

    }


    /* =====================================================
       POST TRIM
    ===================================================== */

    function preparePostTrim() {

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
                file.type.startsWith(
                    "video/"
                )
            ) {

                const video =
                    document.createElement(
                        "video"
                    );

                video.src =
                    URL.createObjectURL(
                        file
                    );

                video.playsInline =
                    true;

                video.muted =
                    true;

                video.loop =
                    true;

                video.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:3/4;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(
                    video
                );

                window.snapzTrimPreviewVideo =
                    video;

                video.play().catch(
                    function () {}
                );

            } else if (file) {

                const img =
                    document.createElement(
                        "img"
                    );

                img.src =
                    URL.createObjectURL(
                        file
                    );

                img.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:3/4;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(
                    img
                );

            }

        }


        loadMusicMetadata(
            function (duration) {

                musicDuration =
                    duration;

                const allowed =
                    Math.min(
                        POST_MAX_DURATION,
                        duration
                    );

                trimStart = 0;
                trimEnd =
                    allowed;

                setupTrim(
                    allowed
                );

            }
        );

    }


    /* =====================================================
       REEL TRIM
    ===================================================== */

    function prepareReelTrim() {

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
                !reelDuration ||
                reelDuration <= 0
            ) {

                reelDuration =
                    reelVideo &&
                    Number.isFinite(
                        reelVideo.duration
                    )
                        ? reelVideo.duration
                        : 0;

            }


            if (
                !reelDuration ||
                reelDuration <= 0
            ) {

                alert(
                    "Reel ki duration detect nahi hui."
                );

                return;

            }


            if (preview) {

                preview.innerHTML = "";

                const video =
                    document.createElement(
                        "video"
                    );

                video.src =
                    reelVideo.currentSrc ||
                    reelVideo.src;

                video.playsInline =
                    true;

                video.muted =
                    true;

                video.loop =
                    true;

                video.style.cssText = `
                    height:100%;
                    max-width:100%;
                    aspect-ratio:9/16;
                    object-fit:cover;
                    background:#000;
                `;

                preview.appendChild(
                    video
                );

                window.snapzTrimPreviewVideo =
                    video;

                video.play().catch(
                    function () {}
                );

            }


            loadMusicMetadata(
                function (duration) {

                    musicDuration =
                        duration;

                    const allowed =
                        Math.min(
                            reelDuration,
                            duration
                        );

                    trimStart = 0;
                    trimEnd =
                        allowed;

                    setupTrim(
                        allowed
                    );

                }
            );

        }


        if (
            reelVideo &&
            reelVideo.readyState >= 1
        ) {

            continueSetup();

        } else if (reelVideo) {

            reelVideo.addEventListener(
                "loadedmetadata",
                function () {

                    continueSetup();

                },
                {
                    once:true
                }
            );

        } else {

            alert(
                "Reel preview nahi mila."
            );

        }

    }


    /* =====================================================
       SETUP TRIM
    ===================================================== */

    

function setupTrim(allowedDuration) {

    const start =
        document.getElementById(
            "snapzTrimStart"
        );

    const end =
        document.getElementById(
            "snapzTrimEnd"
        );


    if (
        !start ||
        !end
    ) {
        return;
    }


    /*
     * FULL MUSIC
     */

    const fullDuration =
        Number.isFinite(musicDuration) &&
        musicDuration > 0
            ? musicDuration
            : 30;


    /*
     * ONLY SELECTION IS LIMITED
     */

    const maxWindow =
        Math.min(
            Number(allowedDuration) || 30,
            fullDuration
        );


    /*
     * BOTH INPUTS REPRESENT
     * COMPLETE SONG
     */

    start.min = 0;
    start.max = fullDuration;
    start.step = 0.01;

    end.min = 0;
    end.max = fullDuration;
    end.step = 0.01;


    /*
     * DEFAULT SELECTION
     */

    trimStart = 0;

    trimEnd =
        maxWindow;


    start.value =
        trimStart;

    end.value =
        trimEnd;


    /*
     * DRAW FULL SONG
     */

    createInstagramWaveform();


    /*
     * DRAW SELECTED WINDOW
     */

    updateInstagramTrimUI();


    updateTrimText();
}




    /* =====================================================
       UPDATE TRIM
    ===================================================== */

    

function updateTrim() {

    const start =
        document.getElementById(
            "snapzTrimStart"
        );

    const end =
        document.getElementById(
            "snapzTrimEnd"
        );


    if (
        !start ||
        !end ||
        !musicDuration
    ) {
        return;
    }


    const duration =
        musicDuration;


    let s =
        parseFloat(
            start.value
        );

    let e =
        parseFloat(
            end.value
        );


    if (!Number.isFinite(s)) {
        s = trimStart;
    }

    if (!Number.isFinite(e)) {
        e = trimEnd;
    }


    /*
     * MAX WINDOW
     */

    let maxAllowed;


    if (
        currentTarget ===
        "post"
    ) {

        maxAllowed =
            Math.min(
                POST_MAX_DURATION ||
                    30,
                duration
            );

    } else {

        const reelLength =
            getCurrentReelDuration();


        maxAllowed =
            Math.min(
                Number(reelLength) || duration,
                duration
            );
    }


    /*
     * START HANDLE
     */

    if (
        document.activeElement ===
        start
    ) {

        s =
            Math.max(
                0,
                Math.min(
                    s,
                    duration - 0.05
                )
            );


        if (
            e - s >
            maxAllowed
        ) {

            s =
                e - maxAllowed;
        }

    }


    /*
     * END HANDLE
     */

    else {

        e =
            Math.max(
                0.05,
                Math.min(
                    e,
                    duration
                )
            );


        if (
            e - s >
            maxAllowed
        ) {

            e =
                s + maxAllowed;
        }
    }


    /*
     * FINAL LIMITS
     */

    s =
        Math.max(
            0,
            Math.min(
                s,
                duration
            )
        );

    e =
        Math.max(
            0,
            Math.min(
                e,
                duration
            )
        );


    if (
        e <= s
    ) {

        e =
            Math.min(
                duration,
                s + 0.05
            );
    }


    trimStart = s;
    trimEnd = e;


    start.value =
        s;

    end.value =
        e;


    updateInstagramTrimUI();
}




    /* =====================================================
       TRIM TEXT
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


    /* =====================================================
       POST TRIM
    ===================================================== */



    /* =====================================================
       MUSIC METADATA
    ===================================================== */

    function loadMusicMetadata(callback) {

        const a =
            new Audio(
                selectedMusic.url
            );

        a.preload =
            "metadata";


        a.addEventListener(
            "loadedmetadata",
            function () {

                if (
                    Number.isFinite(
                        a.duration
                    ) &&
                    a.duration > 0
                ) {

                    callback(
                        a.duration
                    );

                } else {

                    callback(30);

                }

            },
            {
                once:true
            }
        );


        a.addEventListener(
            "error",
            function () {

                console.error(
                    "Music metadata error"
                );

                callback(30);

            },
            {
                once:true
            }
        );

    }


    /* =====================================================
       SETUP TRIM
    ===================================================== */

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
            String(secs)
                .padStart(2,"0")
        );

    }


    /* =====================================================
       PLAY TRIM PREVIEW
    ===================================================== */

    function playTrimPreview() {

        stopAudio();

        if (!selectedMusic) {
            return;
        }


        musicAudio =
            new Audio(
                selectedMusic.url
            );

        musicAudio.preload =
            "auto";

        musicAudio.currentTime =
            trimStart;


        musicAudio.addEventListener(
            "timeupdate",
            function () {

                if (
                    musicAudio &&
                    musicAudio.currentTime >=
                    trimEnd
                ) {

                    musicAudio.pause();

                    musicAudio.currentTime =
                        trimStart;

                }

            }
        );


        musicAudio.play()
            .catch(
                function (error) {

                    console.log(
                        "Preview blocked:",
                        error
                    );

                }
            );


        if (
            currentTarget === "reel" &&
            window.snapzTrimPreviewVideo
        ) {

            const video =
                window.snapzTrimPreviewVideo;

            video.currentTime =
                0;

            video.play().catch(
                function () {}
            );

        }

    }


    /* =====================================================
       STOP AUDIO
    ===================================================== */

    function stopAudio() {

        if (musicAudio) {

            try {

                musicAudio.pause();
                musicAudio.currentTime =
                    0;

            } catch (e) {}

            musicAudio =
                null;

        }

    }


    /* =====================================================
       FINISH TRIM
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

            console.log(
                "SNAPZ POST MUSIC SAVED:",
                data
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

            console.log(
                "SNAPZ REEL MUSIC SAVED:",
                data
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


        const trim =
            document.getElementById(
                "snapzPostReelTrimPanel"
            );

        if (trim) {
            trim.remove();
        }


        closeLibrary();

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
