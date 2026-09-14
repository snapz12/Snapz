/* =========================================================
   SNAPZ FRESH STORY MUSIC SYSTEM
   Completely independent from Post / Reel Music
========================================================= */

(function () {

    "use strict";

    console.log("SNAPZ FRESH STORY MUSIC JS LOADED");


    async function openSnapzStoryMusic() {

        // SNAPZ STORY MUSIC OPEN LOCK
        if (window.snapzStoryMusicOpening === true) {
            console.log(
                "SNAPZ STORY MUSIC OPEN ALREADY IN PROGRESS"
            );
            return;
        }

        window.snapzStoryMusicOpening = true;

        /*
         * =====================================================
         * SNAPZ STORY -> EXISTING POST/REEL MUSIC BRIDGE
         * IMPORTANT:
         * Post/Reel Music JS is NOT modified.
         * Story reuses the existing working Music Library
         * and existing Trim Screen.
         * =====================================================
         */

        if (
            typeof window.openSnapzPostReelMusic === "function"
        ) {

            console.log(
                "SNAPZ STORY MUSIC: USING EXISTING POST/REEL MUSIC PANEL"
            );

            try {

                /*
                 * Clear any previous Post/Reel audio selection.
                 * This prevents the Story bridge from treating
                 * an old selection as a newly selected Story song.
                 */
                window.snapzSelectedAudio = null;

                /*
                 * Existing Post/Reel Music reads selectedFiles.
                 * Story already stores its selected media in
                 * selectedFiles[0], so keep that untouched.
                 */

                window.openSnapzPostReelMusic("post");

                /*
                 * Existing Post/Reel Trim writes:
                 * window.snapzSelectedAudio
                 *
                 * Watch it from Story side and convert it into
                 * the Story Music state.
                 */
                let storyMusicBridgeTimer = null;

                storyMusicBridgeTimer = setInterval(
                    function () {

                        const audio =
                            window.snapzSelectedAudio;

                        if (!audio || !audio.url) {
                            return;
                        }

                        const storyMusic = {
                            id: audio.id,
                            title: audio.title,
                            artist: audio.artist,
                            url: audio.url,
                            start: Number(audio.startTime || 0),
                            end:
                                Number(audio.startTime || 0) +
                                Number(audio.duration || 0),
                            duration: Number(audio.duration || 0),
                            media_duration:
                                Number(audio.duration || 0)
                        };

                        sessionStorage.setItem(
                            "snapz_story_music_fresh",
                            JSON.stringify(storyMusic)
                        );

                        sessionStorage.removeItem(
                            "snapz_story_music"
                        );

                        window.selectedStoryMusic =
                            storyMusic;

                        console.log(
                            "SNAPZ STORY MUSIC BRIDGE SUCCESS =",
                            storyMusic
                        );

                        clearInterval(
                            storyMusicBridgeTimer
                        );

                        storyMusicBridgeTimer = null;

                    },
                    250
                );

                /*
                 * Safety timeout. The bridge only watches for a
                 * short period and does not affect Post/Reel Music.
                 */
                setTimeout(
                    function () {

                        if (storyMusicBridgeTimer) {

                            clearInterval(
                                storyMusicBridgeTimer
                            );

                            storyMusicBridgeTimer = null;

                            console.log(
                                "SNAPZ STORY MUSIC BRIDGE WATCH ENDED"
                            );
                        }

                    },
                    120000
                );

                window.snapzStoryMusicOpening = false;

                return;

            } catch (bridgeError) {

                console.error(
                    "SNAPZ STORY MUSIC BRIDGE ERROR =",
                    bridgeError
                );

                window.snapzStoryMusicOpening = false;
            }
        }

        try {

            let panel =
                document.getElementById(
                    "snapzStoryMusicPage"
                );

            // Remove accidental duplicate panels.
            const panels =
                document.querySelectorAll(
                    "#snapzStoryMusicPage"
                );

            if (panels.length > 1) {

                console.log(
                    "SNAPZ STORY MUSIC DUPLICATE PANELS =",
                    panels.length
                );

                for (
                    let i = 1;
                    i < panels.length;
                    i++
                ) {
                    panels[i].remove();
                }

                panel =
                    document.getElementById(
                        "snapzStoryMusicPage"
                    );
            }

            if (!panel) {

                const response =
                    await fetch("/story_music");

                if (!response.ok) {
                    throw new Error(
                        "Story Music page load failed"
                    );
                }

                const html =
                    await response.text();

                const temp =
                    document.createElement("div");

                temp.innerHTML = html;

                const freshPanel =
                    temp.querySelector(
                        "#snapzStoryMusicPage"
                    );

                if (!freshPanel) {
                    throw new Error(
                        "snapzStoryMusicPage not found"
                    );
                }

                /*
                 * Load Story Music CSS from
                 * templates/story_music.html
                 */
                const storyMusicStyles =
                    temp.querySelectorAll("style");

                storyMusicStyles.forEach(function (style) {

                    if (
                        document.head.querySelector(
                            'style[data-snapz-story-music-style="1"]'
                        )
                    ) {
                        return;
                    }

                    const styleCopy =
                        document.createElement("style");

                    styleCopy.setAttribute(
                        "data-snapz-story-music-style",
                        "1"
                    );

                    styleCopy.textContent =
                        style.textContent;

                    document.head.appendChild(
                        styleCopy
                    );
                });

                // Final duplicate protection
                const existingPanel =
                    document.getElementById(
                        "snapzStoryMusicPage"
                    );

                if (existingPanel) {

                    panel = existingPanel;

                } else {

                    document.body.appendChild(
                        freshPanel
                    );

                    panel =
                        document.getElementById(
                            "snapzStoryMusicPage"
                        );
                }

                bindCloseButton();
            }

            if (!panel) {
                throw new Error(
                    "Story Music panel unavailable"
                );
            }

            panel.style.display = "flex";

            document.body.style.overflow = "hidden";

            console.log(
                "SNAPZ STORY MUSIC PANEL COUNT =",
                document.querySelectorAll(
                    "#snapzStoryMusicPage"
                ).length
            );

            await loadStoryMusicLibrary();

            console.log(
                "SNAPZ STORY MUSIC LIST AFTER LOAD =",
                document.querySelectorAll(
                    "#snapzStoryMusicList"
                ).length
            );

            bindStoryMusicUpload();
            bindStoryMusicPlayback();
            bindStoryMusicSearch();
            bindStoryMusicSelection();
            bindStoryMusicTrimNavigation();

            console.log(
                "SNAPZ STORY MUSIC PANEL OPENED"
            );

        } catch (error) {

            console.error(
                "SNAPZ STORY MUSIC OPEN ERROR =",
                error
            );

            alert(
                "Story Music load nahi ho saka."
            );

        } finally {

            window.snapzStoryMusicOpening = false;

        }
    }


    async function loadStoryMusicLibrary() {

        const list =
            document.getElementById(
                "snapzStoryMusicList"
            );

        if (!list) {
            return;
        }

        try {

            const response =
                await fetch("/story_music_library");

            if (!response.ok) {
                throw new Error(
                    "Story Music library load failed"
                );
            }

            const songs =
                await response.json();

            if (!songs.length) {

                list.innerHTML = `
                    <div style="
                        text-align:center;
                        color:#888;
                        padding:40px 20px;
                    ">
                        No music uploaded yet
                    </div>
                `;

                return;
            }

            list.innerHTML = songs.map(function (song) {

                return `
                    <div
                        class="snapz-story-music-item"
                        data-music-id="${song.id}"
                    >

                        <div class="snapz-story-music-cover">
                            ${
                                song.cover_url
                                    ? `<img src="${song.cover_url}" alt="">`
                                    : "🎵"
                            }
                        </div>

                        <div class="snapz-story-music-info">

                            <div class="snapz-story-music-title">
                                ${song.title || "Untitled"}
                            </div>

                            <div class="snapz-story-music-artist">
                                ${song.artist || "Original Audio"}
                            </div>

                        </div>

                        <button
                            type="button"
                            class="snapz-story-music-play"
                            data-audio-url="${song.audio_url}"
                        >
                            ▶
                        </button>

                    </div>
                `;

            }).join("");

        } catch (error) {

            console.error(
                "STORY MUSIC LIBRARY ERROR =",
                error
            );

            list.innerHTML = `
                <div style="
                    text-align:center;
                    color:#f66;
                    padding:40px 20px;
                ">
                    Music library load failed
                </div>
            `;
        }
    }


    function getStoryMediaDuration() {

        try {

            if (
                typeof mode !== "undefined" &&
                mode === "story" &&
                typeof selectedFile !== "undefined" &&
                selectedFile
            ) {

                if (
                    selectedFile.type &&
                    selectedFile.type.startsWith("video/")
                ) {

                    const video =
                        document.getElementById("storyVideo");

                    if (video && video.duration) {
                        return Math.min(
                            Number(video.duration) || 0,
                            30
                        );
                    }

                    const previewVideo =
                        document.getElementById("previewVideo");

                    if (
                        previewVideo &&
                        previewVideo.duration
                    ) {
                        return Math.min(
                            Number(previewVideo.duration) || 0,
                            30
                        );
                    }

                    return 30;
                }

                if (
                    selectedFile.type &&
                    selectedFile.type.startsWith("image/")
                ) {
                    return 15;
                }
            }

        } catch (error) {

            console.log(
                "STORY MEDIA DURATION ERROR =",
                error
            );
        }

        return 15;
    }


    function formatStoryMusicTime(seconds) {

        const total =
            Math.max(
                0,
                Math.floor(
                    Number(seconds) || 0
                )
            );

        const minutes =
            Math.floor(total / 60);

        const secs =
            total % 60;

        return (
            minutes +
            ":" +
            String(secs).padStart(2, "0")
        );
    }


    function updateStoryMusicTrimUI() {

        const timeline =
            document.getElementById(
                "snapzStoryMusicTrimTimeline"
            );

        const selected =
            timeline
                ? timeline.querySelector(
                    ".snapz-story-music-trim-selected"
                )
                : null;

        const startTime =
            document.getElementById(
                "snapzStoryMusicTrimStartTime"
            );

        const endTime =
            document.getElementById(
                "snapzStoryMusicTrimEndTime"
            );

        const state =
            window.snapzStoryMusicTrimState;

        if (
            !timeline ||
            !selected ||
            !state
        ) {
            return;
        }

        const duration =
            Number(state.duration) || 0;

        const windowDuration =
            Number(state.windowDuration) || 0;

        if (
            !duration ||
            !windowDuration
        ) {
            return;
        }

        const startPercent =
            (state.start / duration) * 100;

        const endPercent =
            (state.end / duration) * 100;

        selected.style.left =
            startPercent + "%";

        selected.style.right =
            (100 - endPercent) + "%";

        if (startTime) {

            startTime.textContent =
                formatStoryMusicTime(
                    state.start
                );
        }

        if (endTime) {

            endTime.textContent =
                formatStoryMusicTime(
                    state.end
                );
        }
    }


    function setupStoryMusicMediaPreview() {

        const mediaBox =
            document.getElementById(
                "snapzStoryMusicTrimMedia"
            );

        if (!mediaBox) {
            return;
        }

        mediaBox.innerHTML = "";

        let file = null;

        try {

            if (
                typeof selectedFile !== "undefined" &&
                selectedFile
            ) {
                file = selectedFile;
            }

        } catch (error) {

            console.log(
                "STORY MEDIA LOOKUP ERROR =",
                error
            );
        }

        if (!file) {
            return;
        }

        const objectUrl =
            URL.createObjectURL(file);

        if (
            file.type &&
            file.type.startsWith("video/")
        ) {

            const video =
                document.createElement("video");

            video.src = objectUrl;
            video.autoplay = true;
            video.loop = true;
            video.playsInline = true;
            video.muted = true;
            video.controls = false;

            video.style.width = "100%";
            video.style.height = "100%";
            video.style.objectFit = "contain";
            video.style.display = "block";

            mediaBox.appendChild(video);

            window.snapzStoryMusicTrimMedia =
                video;

            video.addEventListener(
                "loadedmetadata",
                function () {

                    const state =
                        window.snapzStoryMusicTrimState;

                    if (!state) {
                        return;
                    }

                    state.mediaDuration =
                        Math.min(
                            Number(video.duration) || 0,
                            30
                        );

                    if (
                        state.mediaDuration > 0
                    ) {

                        state.windowDuration =
                            state.mediaDuration;

                        state.end =
                            state.start +
                            state.windowDuration;

                        updateStoryMusicTrimUI();
                    }
                }
            );

            video.play().catch(
                function (error) {

                    console.log(
                        "STORY TRIM VIDEO PLAY ERROR =",
                        error
                    );
                }
            );

        } else {

            const img =
                document.createElement("img");

            img.src = objectUrl;

            img.style.width = "100%";
            img.style.height = "100%";
            img.style.objectFit = "contain";
            img.style.display = "block";

            mediaBox.appendChild(img);

            window.snapzStoryMusicTrimMedia =
                img;
        }

        console.log(
            "SNAPZ STORY MUSIC MEDIA PREVIEW READY =",
            file.name
        );
    }


    function openStoryMusicTrim() {

        const library =
            document.getElementById(
                "snapzStoryMusicList"
            );

        const trim =
            document.getElementById(
                "snapzStoryMusicTrim"
            );

        const music =
            window.selectedStoryMusic;

        if (
            !trim ||
            !music ||
            !music.audio_url
        ) {
            return;
        }

        const title =
            document.getElementById(
                "snapzStoryMusicTrimSongTitle"
            );

        const artist =
            document.getElementById(
                "snapzStoryMusicTrimSongArtist"
            );

        if (title) {
            title.textContent =
                music.title || "Untitled";
        }

        if (artist) {
            artist.textContent =
                music.artist || "Original Audio";
        }

        if (library) {
            library.style.display = "none";
        }

        trim.style.display = "flex";

        setupStoryMusicMediaPreview();

        bindStoryMusicTrimEngine();

        console.log(
            "SNAPZ STORY MUSIC TRIM OPENED =",
            music
        );
    }


    function closeStoryMusicTrim() {

        const trim =
            document.getElementById(
                "snapzStoryMusicTrim"
            );

        const library =
            document.getElementById(
                "snapzStoryMusicList"
            );

        if (
            window.snapzStoryMusicTrimAudio
        ) {
            window.snapzStoryMusicTrimAudio.pause();
        }

        if (
            window.snapzStoryMusicTrimMedia &&
            window.snapzStoryMusicTrimMedia.tagName ===
                "VIDEO"
        ) {
            window.snapzStoryMusicTrimMedia.pause();
        }

        if (trim) {
            trim.style.display = "none";
        }

        if (library) {
            library.style.display = "";
        }

        console.log(
            "SNAPZ STORY MUSIC TRIM CLOSED"
        );
    }


    function setupStoryMusicTrimAudio() {

        const music =
            window.selectedStoryMusic;

        if (
            !music ||
            !music.audio_url
        ) {
            return;
        }

        if (
            window.snapzStoryMusicTrimAudio
        ) {
            window.snapzStoryMusicTrimAudio.pause();

            window.snapzStoryMusicTrimAudio.src =
                "";
        }

        const audio =
            new Audio();

        audio.preload = "metadata";
        audio.src = music.audio_url;

        window.snapzStoryMusicTrimAudio =
            audio;

        const mediaDuration =
            getStoryMediaDuration();

        window.snapzStoryMusicTrimState = {
            duration: 0,
            start: 0,
            end: 0,
            windowDuration: mediaDuration,
            mediaDuration: mediaDuration
        };

        const playButton =
            document.getElementById(
                "snapzStoryMusicTrimPlay"
            );

        audio.addEventListener(
            "loadedmetadata",
            function () {

                const duration =
                    Number(audio.duration) || 0;

                if (!duration) {
                    return;
                }

                const state =
                    window.snapzStoryMusicTrimState;

                if (!state) {
                    return;
                }

                state.duration =
                    duration;

                state.windowDuration =
                    Math.min(
                        state.windowDuration,
                        duration
                    );

                state.start = 0;

                state.end =
                    state.windowDuration;

                audio.currentTime = 0;

                updateStoryMusicTrimUI();

                console.log(
                    "STORY MUSIC FULL SONG DURATION =",
                    duration
                );

                console.log(
                    "STORY MUSIC FIXED WINDOW =",
                    state.windowDuration
                );
            }
        );

        audio.addEventListener(
            "timeupdate",
            function () {

                const state =
                    window.snapzStoryMusicTrimState;

                if (!state) {
                    return;
                }

                if (
                    audio.currentTime >=
                    state.end
                ) {

                    audio.pause();

                    audio.currentTime =
                        state.start;

                    if (playButton) {
                        playButton.textContent =
                            "▶";
                    }
                }
            }
        );

        audio.addEventListener(
            "ended",
            function () {

                if (playButton) {
                    playButton.textContent =
                        "▶";
                }
            }
        );

        if (playButton) {

            playButton.onclick =
                function () {

                    const state =
                        window.snapzStoryMusicTrimState;

                    if (
                        !state ||
                        !state.duration
                    ) {
                        return;
                    }

                    if (audio.paused) {

                        if (
                            audio.currentTime <
                                state.start ||
                            audio.currentTime >=
                                state.end
                        ) {
                            audio.currentTime =
                                state.start;
                        }

                        audio.play()
                            .then(
                                function () {

                                    playButton.textContent =
                                        "❚❚";
                                }
                            )
                            .catch(
                                function (error) {

                                    console.error(
                                        "STORY MUSIC TRIM PLAY ERROR =",
                                        error
                                    );

                                    playButton.textContent =
                                        "▶";
                                }
                            );

                    } else {

                        audio.pause();

                        playButton.textContent =
                            "▶";
                    }
                };
        }

        console.log(
            "SNAPZ STORY MUSIC TRIM AUDIO READY"
        );
    }


    function bindStoryMusicTrimHandles() {

        const timeline =
            document.getElementById(
                "snapzStoryMusicTrimTimeline"
            );

        const selected =
            timeline
                ? timeline.querySelector(
                    ".snapz-story-music-trim-selected"
                )
                : null;

        if (
            !timeline ||
            !selected
        ) {
            return;
        }

        if (
            timeline.dataset.snapzTrimCenterBound === "1"
        ) {
            return;
        }

        timeline.dataset.snapzTrimCenterBound =
            "1";

        let dragging = false;
        let pointerId = null;
        let dragOffset = 0;

        selected.style.cursor =
            "grab";

        function updateFromPointer(clientX) {

            const state =
                window.snapzStoryMusicTrimState;

            if (
                !state ||
                !state.duration ||
                !state.windowDuration
            ) {
                return;
            }

            const rect =
                timeline.getBoundingClientRect();

            if (!rect.width) {
                return;
            }

            const pointerTime =
                (
                    (clientX - rect.left) /
                    rect.width
                ) * state.duration;

            let newStart =
                pointerTime -
                dragOffset;

            const maxStart =
                Math.max(
                    0,
                    state.duration -
                    state.windowDuration
                );

            newStart =
                Math.max(
                    0,
                    Math.min(
                        maxStart,
                        newStart
                    )
                );

            state.start =
                newStart;

            state.end =
                newStart +
                state.windowDuration;

            updateStoryMusicTrimUI();

            if (
                window.snapzStoryMusicTrimAudio
            ) {
                window.snapzStoryMusicTrimAudio.currentTime =
                    state.start;
            }
        }

        selected.addEventListener(
            "pointerdown",
            function (e) {

                e.preventDefault();
                e.stopPropagation();

                const state =
                    window.snapzStoryMusicTrimState;

                if (
                    !state ||
                    !state.duration ||
                    !state.windowDuration
                ) {
                    return;
                }

                const rect =
                    timeline.getBoundingClientRect();

                const pointerTime =
                    (
                        (e.clientX - rect.left) /
                        rect.width
                    ) * state.duration;

                const selectedCenter =
                    state.start +
                    (
                        state.windowDuration /
                        2
                    );

                dragOffset =
                    pointerTime -
                    selectedCenter;

                dragging = true;
                pointerId =
                    e.pointerId;

                selected.setPointerCapture(
                    e.pointerId
                );

                selected.style.cursor =
                    "grabbing";
            },
            false
        );

        selected.addEventListener(
            "pointermove",
            function (e) {

                if (
                    !dragging ||
                    e.pointerId !== pointerId
                ) {
                    return;
                }

                e.preventDefault();

                updateFromPointer(
                    e.clientX
                );
            },
            false
        );

        function stopDrag(e) {

            if (
                pointerId !== null &&
                e.pointerId !== pointerId
            ) {
                return;
            }

            dragging = false;
            pointerId = null;

            selected.style.cursor =
                "grab";
        }

        selected.addEventListener(
            "pointerup",
            stopDrag,
            false
        );

        selected.addEventListener(
            "pointercancel",
            stopDrag,
            false
        );

        console.log(
            "SNAPZ STORY MUSIC CENTER DRAG READY"
        );
    }


    function bindStoryMusicTrimApply() {

        const applyButton =
            document.getElementById(
                "snapzStoryMusicTrimApply"
            );

        if (!applyButton) {
            return;
        }

        if (
            applyButton.dataset.snapzStoryMusicApplyBound ===
            "1"
        ) {
            return;
        }

        applyButton.dataset.snapzStoryMusicApplyBound =
            "1";

        applyButton.addEventListener(
            "click",
            function () {

                const music =
                    window.selectedStoryMusic;

                const state =
                    window.snapzStoryMusicTrimState;

                if (
                    !music ||
                    !state ||
                    !state.duration
                ) {
                    return;
                }

                const savedMusic = {

                    id:
                        music.id,

                    title:
                        music.title,

                    artist:
                        music.artist,

                    url:
                        music.audio_url,

                    start:
                        Number(state.start) || 0,

                    end:
                        Number(state.end) || 0,

                    duration:
                        Number(state.windowDuration) || 0,

                    media_duration:
                        Number(state.mediaDuration) || 0
                };

                window.selectedStoryMusic =
                    Object.assign(
                        {},
                        music,
                        {
                            url:
                                savedMusic.url,
                            start:
                                savedMusic.start,
                            end:
                                savedMusic.end,
                            duration:
                                savedMusic.duration,
                            media_duration:
                                savedMusic.media_duration
                        }
                    );

                sessionStorage.setItem(
                    "snapz_story_music_fresh",
                    JSON.stringify(
                        savedMusic
                    )
                );

                sessionStorage.removeItem(
                    "snapz_story_music"
                );

                if (
                    window.snapzStoryMusicTrimAudio
                ) {
                    window.snapzStoryMusicTrimAudio.pause();
                }

                const media =
                    window.snapzStoryMusicTrimMedia;

                if (
                    media &&
                    media.tagName === "VIDEO"
                ) {
                    media.muted = true;
                }

                closeStoryMusicTrim();

                const trimButton =
                    document.getElementById(
                        "snapzStoryMusicButton"
                    );

                if (trimButton) {
                    trimButton.classList.add(
                        "selected"
                    );
                }

                console.log(
                    "SNAPZ STORY MUSIC APPLY SUCCESS =",
                    savedMusic
                );
            },
            false
        );
    }


    function bindStoryMusicTrimEngine() {

        bindStoryMusicTrimHandles();

        bindStoryMusicTrimApply();

        setupStoryMusicTrimAudio();

        console.log(
            "SNAPZ STORY MUSIC TRIM ENGINE READY"
        );
    }


    function bindStoryMusicTrimNavigation() {

        const backButton =
            document.getElementById(
                "snapzStoryMusicTrimBack"
            );

        const trim =
            document.getElementById(
                "snapzStoryMusicTrim"
            );

        if (!backButton || !trim) {
            return;
        }

        if (
            backButton.dataset.snapzStoryMusicTrimBound === "1"
        ) {
            return;
        }

        backButton.dataset.snapzStoryMusicTrimBound = "1";

        backButton.addEventListener(
            "click",
            function () {
                closeStoryMusicTrim();
            },
            false
        );
    }


    function bindStoryMusicSelection() {

        const list =
            document.getElementById(
                "snapzStoryMusicList"
            );

        if (!list) {
            return;
        }

        if (
            list.dataset.snapzStoryMusicSelectionBound === "1"
        ) {
            return;
        }

        list.dataset.snapzStoryMusicSelectionBound = "1";

        list.addEventListener(
            "click",
            function (e) {

                if (
                    e.target.closest(
                        ".snapz-story-music-play"
                    )
                ) {
                    return;
                }

                const item =
                    e.target.closest(
                        ".snapz-story-music-item"
                    );

                if (!item) {
                    return;
                }

                const musicId =
                    item.dataset.musicId;

                const title =
                    item.querySelector(
                        ".snapz-story-music-title"
                    );

                const artist =
                    item.querySelector(
                        ".snapz-story-music-artist"
                    );

                const playButton =
                    item.querySelector(
                        ".snapz-story-music-play"
                    );

                const audioUrl =
                    playButton
                        ? playButton.dataset.audioUrl
                        : "";

                if (!musicId || !audioUrl) {
                    return;
                }

                window.selectedStoryMusic = {
                    id: musicId,
                    title: title
                        ? title.textContent.trim()
                        : "Untitled",
                    artist: artist
                        ? artist.textContent.trim()
                        : "Original Audio",
                    audio_url: audioUrl
                };

                list
                    .querySelectorAll(
                        ".snapz-story-music-item"
                    )
                    .forEach(function (row) {
                        row.classList.remove(
                            "selected"
                        );
                    });

                item.classList.add("selected");

                openStoryMusicTrim();

                console.log(
                    "SNAPZ STORY MUSIC SELECTED =",
                    window.selectedStoryMusic
                );

            },
            false
        );
    }


    function bindStoryMusicSearch() {

        const searchInput =
            document.getElementById(
                "snapzStoryMusicSearch"
            );

        const list =
            document.getElementById(
                "snapzStoryMusicList"
            );

        if (!searchInput || !list) {
            return;
        }

        if (
            searchInput.dataset.snapzStoryMusicSearchBound === "1"
        ) {
            return;
        }

        searchInput.dataset.snapzStoryMusicSearchBound = "1";

        searchInput.addEventListener(
            "input",
            function () {

                const query =
                    this.value
                        .trim()
                        .toLowerCase();

                const items =
                    list.querySelectorAll(
                        ".snapz-story-music-item"
                    );

                items.forEach(function (item) {

                    const title =
                        item.querySelector(
                            ".snapz-story-music-title"
                        );

                    const artist =
                        item.querySelector(
                            ".snapz-story-music-artist"
                        );

                    const titleText =
                        title
                            ? title.textContent.toLowerCase()
                            : "";

                    const artistText =
                        artist
                            ? artist.textContent.toLowerCase()
                            : "";

                    const matched =
                        !query ||
                        titleText.includes(query) ||
                        artistText.includes(query);

                    item.style.display =
                        matched ? "flex" : "none";
                });
            },
            false
        );
    }


    function bindStoryMusicPlayback() {

        const list =
            document.getElementById(
                "snapzStoryMusicList"
            );

        if (!list) {
            return;
        }

        if (
            list.dataset.snapzStoryMusicPlaybackBound === "1"
        ) {
            return;
        }

        list.dataset.snapzStoryMusicPlaybackBound = "1";

        list.addEventListener(
            "click",
            function (e) {

                const button =
                    e.target.closest(
                        ".snapz-story-music-play"
                    );

                if (!button) {
                    return;
                }

                e.preventDefault();
                e.stopPropagation();

                const audioUrl =
                    button.dataset.audioUrl;

                if (!audioUrl) {
                    return;
                }

                if (
                    window.snapzStoryMusicAudio &&
                    window.snapzStoryMusicAudio.src === audioUrl
                ) {

                    const audio =
                        window.snapzStoryMusicAudio;

                    if (audio.paused) {
                        audio.play();
                        button.textContent = "❚❚";
                    } else {
                        audio.pause();
                        button.textContent = "▶";
                    }

                    return;
                }

                if (window.snapzStoryMusicAudio) {
                    window.snapzStoryMusicAudio.pause();
                }

                const audio =
                    new Audio(audioUrl);

                window.snapzStoryMusicAudio =
                    audio;

                document
                    .querySelectorAll(
                        ".snapz-story-music-play"
                    )
                    .forEach(function (btn) {
                        btn.textContent = "▶";
                    });

                button.textContent = "❚❚";

                audio.addEventListener(
                    "ended",
                    function () {
                        button.textContent = "▶";
                    }
                );

                audio.play().catch(function (error) {

                    console.error(
                        "STORY MUSIC PLAY ERROR =",
                        error
                    );

                    button.textContent = "▶";

                });

            },
            false
        );
    }


    function bindStoryMusicUpload() {

        const uploadButton =
            document.getElementById(
                "snapzStoryMusicUploadButton"
            );

        const uploadInput =
            document.getElementById(
                "snapzStoryMusicUploadInput"
            );

        if (!uploadButton || !uploadInput) {
            console.log(
                "SNAPZ STORY MUSIC UPLOAD ELEMENTS NOT FOUND"
            );
            return;
        }

        if (
            window.snapzStoryMusicUploadChangeBound === true
        ) {
            return;
        }

        window.snapzStoryMusicUploadChangeBound = true;

        console.log(
            "SNAPZ STORY MUSIC UPLOAD CHANGE HANDLER READY"
        );

        document.addEventListener(
            "change",
            async function (event) {

                const input = event.target;

                if (
                    !input ||
                    input.id !==
                        "snapzStoryMusicUploadInput"
                ) {
                    return;
                }

                console.log(
                    "===== SNAPZ STORY MUSIC FILE CHANGE ====="
                );

                const file =
                    input.files &&
                    input.files[0];

                console.log(
                    "STORY MUSIC SELECTED FILE =",
                    file ? file.name : null
                );

                if (!file) {
                    console.log(
                        "STORY MUSIC NO FILE RECEIVED"
                    );
                    return;
                }

                const formData =
                    new FormData();

                formData.append(
                    "music",
                    file
                );

                uploadButton.disabled = true;
                uploadButton.textContent =
                    "Uploading...";

                try {

                    console.log(
                        "STORY MUSIC UPLOAD FETCH START"
                    );

                    const response =
                        await fetch(
                            "/upload_story_music",
                            {
                                method: "POST",
                                body: formData
                            }
                        );

                    console.log(
                        "STORY MUSIC UPLOAD HTTP STATUS =",
                        response.status
                    );

                    const result =
                        await response.json();

                    console.log(
                        "STORY MUSIC UPLOAD RESPONSE =",
                        result
                    );

                    if (
                        !response.ok ||
                        result.status !== "success"
                    ) {
                        throw new Error(
                            result.message ||
                            "Upload failed"
                        );
                    }

                    console.log(
                        "STORY MUSIC UPLOAD SUCCESS =",
                        result
                    );

                    await loadStoryMusicLibrary();

                } catch (error) {

                    console.error(
                        "STORY MUSIC UPLOAD ERROR =",
                        error
                    );

                    alert(
                        error.message ||
                        "Music upload failed."
                    );

                } finally {

                    uploadButton.disabled = false;
                    uploadButton.textContent =
                        "+ Upload Music";

                    input.value = "";
                }
            },
            false
        );
    }

    function closeSnapzStoryMusic() {

        const panel =
            document.getElementById("snapzStoryMusicPage");

        if (!panel) {
            return;
        }

        panel.style.display = "none";

        document.body.style.overflow = "";

        console.log(
            "SNAPZ STORY MUSIC PANEL CLOSED"
        );
    }


    function bindStoryMusicButton() {

        const button =
            document.getElementById(
                "snapzStoryMusicButton"
            );

        if (!button) {
            return;
        }

        if (
            button.dataset.snapzStoryMusicBound === "1"
        ) {
            return;
        }

        button.dataset.snapzStoryMusicBound = "1";

        button.addEventListener(
            "click",
            function (event) {

                event.preventDefault();
                event.stopPropagation();

                openSnapzStoryMusic();

            },
            false
        );

        console.log(
            "SNAPZ STORY MUSIC BUTTON READY"
        );
    }


    function bindCloseButton() {

        const button =
            document.getElementById(
                "snapzStoryMusicClose"
            );

        if (!button) {
            return;
        }

        if (
            button.dataset.snapzStoryMusicBound === "1"
        ) {
            return;
        }

        button.dataset.snapzStoryMusicBound = "1";

        button.addEventListener(
            "click",
            function () {
                closeSnapzStoryMusic();
            },
            false
        );
    }


    function initStoryMusic() {

        bindStoryMusicButton();
        bindCloseButton();

    }


    window.openSnapzStoryMusic =
        openSnapzStoryMusic;

    window.closeSnapzStoryMusic =
        closeSnapzStoryMusic;


    if (document.readyState === "loading") {

        document.addEventListener(
            "DOMContentLoaded",
            initStoryMusic
        );

    } else {

        initStoryMusic();

    }


})();
