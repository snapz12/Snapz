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

        console.log(
            "SNAPZ STORY MUSIC PANEL OPENED"
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
