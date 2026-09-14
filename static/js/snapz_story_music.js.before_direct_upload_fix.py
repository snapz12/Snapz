/* =========================================================
   SNAPZ FRESH STORY MUSIC SYSTEM
   Completely independent from Post / Reel Music
========================================================= */

(function () {

    "use strict";

    console.log("SNAPZ FRESH STORY MUSIC JS LOADED");


    async function openSnapzStoryMusic() {

        let panel =
            document.getElementById(
                "snapzStoryMusicPage"
            );

        /*
         * Panel is kept in a separate template:
         * templates/story_music.html
         */

        if (!panel) {

            try {

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

                document.body.appendChild(
                    freshPanel
                );

                panel =
                    document.getElementById(
                        "snapzStoryMusicPage"
                    );

                bindCloseButton();

            } catch (error) {

                console.error(
                    "SNAPZ STORY MUSIC LOAD ERROR =",
                    error
                );

                alert(
                    "Story Music load nahi ho saka."
                );

                return;
            }
        }

        panel.style.display = "flex";

        document.body.style.overflow = "hidden";

        await loadStoryMusicLibrary();
        bindStoryMusicUpload();
        bindStoryMusicPlayback();
        bindStoryMusicSearch();
        bindStoryMusicSelection();
        bindStoryMusicTrimNavigation();

        console.log(
            "SNAPZ STORY MUSIC PANEL OPENED"
        );
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

        if (!trim || !music) {
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


    function formatStoryMusicTime(seconds) {

        seconds = Number(seconds) || 0;

        const minutes =
            Math.floor(seconds / 60);

        const remaining =
            Math.floor(seconds % 60);

        return (
            minutes +
            ":" +
            String(remaining).padStart(2, "0")
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

        const startHandle =
            document.getElementById(
                "snapzStoryMusicTrimStart"
            );

        const endHandle =
            document.getElementById(
                "snapzStoryMusicTrimEnd"
            );

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

        if (!timeline || !selected || !state) {
            return;
        }

        const duration =
            state.duration || 0;

        if (!duration) {
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

        if (startHandle) {
            startHandle.style.left =
                "calc(" +
                startPercent +
                "% - 1px)";
        }

        if (endHandle) {
            endHandle.style.right =
                "calc(" +
                (100 - endPercent) +
                "% - 1px)";
        }

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


    function setupStoryMusicTrimAudio() {

        const music =
            window.selectedStoryMusic;

        if (!music || !music.audio_url) {
            return;
        }

        if (
            window.snapzStoryMusicTrimAudio
        ) {
            window.snapzStoryMusicTrimAudio.pause();
            window.snapzStoryMusicTrimAudio.src = "";
        }

        const audio =
            new Audio();

        audio.preload = "metadata";
        audio.src = music.audio_url;

        window.snapzStoryMusicTrimAudio =
            audio;

        window.snapzStoryMusicTrimState = {
            duration: 0,
            start: 0,
            end: 0
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

                const maxDuration =
                    Math.min(duration, 30);

                window.snapzStoryMusicTrimState.duration =
                    duration;

                window.snapzStoryMusicTrimState.start =
                    0;

                window.snapzStoryMusicTrimState.end =
                    maxDuration;

                audio.currentTime = 0;

                updateStoryMusicTrimUI();

                console.log(
                    "STORY MUSIC TRIM DURATION =",
                    duration
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

                    if (!state || !state.duration) {
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
                            .then(function () {

                                playButton.textContent =
                                    "❚❚";

                            })
                            .catch(function (error) {

                                console.error(
                                    "STORY MUSIC TRIM PLAY ERROR =",
                                    error
                                );

                            });

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

        const startHandle =
            document.getElementById(
                "snapzStoryMusicTrimStart"
            );

        const endHandle =
            document.getElementById(
                "snapzStoryMusicTrimEnd"
            );

        if (
            !timeline ||
            !startHandle ||
            !endHandle
        ) {
            return;
        }

        if (
            timeline.dataset.snapzTrimHandlesBound === "1"
        ) {
            return;
        }

        timeline.dataset.snapzTrimHandlesBound = "1";

        function dragHandle(handle, isStart) {

            let dragging = false;

            function updateFromPointer(clientX) {

                const state =
                    window.snapzStoryMusicTrimState;

                if (!state || !state.duration) {
                    return;
                }

                const rect =
                    timeline.getBoundingClientRect();

                let percent =
                    (clientX - rect.left) /
                    rect.width;

                percent =
                    Math.max(
                        0,
                        Math.min(1, percent)
                    );

                const time =
                    percent * state.duration;

                const minimumGap =
                    Math.min(
                        0.1,
                        state.duration
                    );

                if (isStart) {

                    state.start =
                        Math.min(
                            time,
                            state.end - minimumGap
                        );

                    state.start =
                        Math.max(
                            0,
                            state.start
                        );

                } else {

                    state.end =
                        Math.max(
                            time,
                            state.start + minimumGap
                        );

                    state.end =
                        Math.min(
                            state.duration,
                            state.end
                        );
                }

                updateStoryMusicTrimUI();
            }

            handle.addEventListener(
                "pointerdown",
                function (e) {

                    e.preventDefault();

                    dragging = true;

                    handle.setPointerCapture(
                        e.pointerId
                    );

                },
                false
            );

            handle.addEventListener(
                "pointermove",
                function (e) {

                    if (!dragging) {
                        return;
                    }

                    updateFromPointer(
                        e.clientX
                    );
                },
                false
            );

            handle.addEventListener(
                "pointerup",
                function () {
                    dragging = false;
                },
                false
            );

            handle.addEventListener(
                "pointercancel",
                function () {
                    dragging = false;
                },
                false
            );
        }

        dragHandle(
            startHandle,
            true
        );

        dragHandle(
            endHandle,
            false
        );

        console.log(
            "SNAPZ STORY MUSIC TRIM HANDLES READY"
        );
    }


    function bindStoryMusicTrimEngine() {

        bindStoryMusicTrimHandles();

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
            return;
        }

        if (
            uploadButton.dataset.snapzStoryMusicUploadBound === "1"
        ) {
            return;
        }

        uploadButton.dataset.snapzStoryMusicUploadBound = "1";

        uploadButton.addEventListener(
            "click",
            function () {
                uploadInput.click();
            }
        );

        uploadInput.addEventListener(
            "change",
            async function () {

                const file =
                    this.files && this.files[0];

                if (!file) {
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

                    const response =
                        await fetch(
                            "/upload_story_music",
                            {
                                method: "POST",
                                body: formData
                            }
                        );

                    const result =
                        await response.json();

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
                        "Music upload nahi ho saka."
                    );

                } finally {

                    uploadButton.disabled = false;

                    uploadButton.textContent =
                        "Upload Music";

                    uploadInput.value = "";
                }
            }
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
