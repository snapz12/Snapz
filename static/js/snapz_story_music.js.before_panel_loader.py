/* =========================================================
   SNAPZ FRESH STORY MUSIC SYSTEM
   Completely independent from Post / Reel Music
========================================================= */

(function () {

    "use strict";

    console.log("SNAPZ FRESH STORY MUSIC JS LOADED");


    function openSnapzStoryMusic() {

        const panel =
            document.getElementById("snapzStoryMusicPage");

        if (!panel) {
            console.error(
                "SNAPZ STORY MUSIC PANEL NOT FOUND"
            );
            return;
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
