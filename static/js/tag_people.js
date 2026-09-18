/* =========================================================
   SLOVZAN — TAG PEOPLE
   Clean standalone implementation
   Maximum 5 people
========================================================= */

(function () {

    "use strict";

    const MAX_TAGS = 5;

    let selectedTags = [];


    /* =====================================================
       CSS
    ===================================================== */

    function injectStyles() {

        if (document.getElementById("slovzanTagPeopleStyle")) {
            return;
        }

        const style = document.createElement("style");

        style.id = "slovzanTagPeopleStyle";

        style.textContent = `

        #slovzanTagPeopleModal {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            bottom: 0 !important;

            width: 100vw !important;
            height: 100vh !important;

            display: none;

            align-items: flex-end;
            justify-content: center;

            background: rgba(0,0,0,.72);

            z-index: 2147483647 !important;

            visibility: visible;
            opacity: 1;

            box-sizing: border-box;
        }


        #slovzanTagPeoplePanel {

            width: 100%;
            max-width: 520px;

            max-height: 85vh;

            background: #111318;
            color: #fff;

            border-radius: 24px 24px 0 0;

            overflow: hidden;

            box-shadow:
                0 -10px 40px rgba(0,0,0,.55);

            box-sizing: border-box;
        }


        .slovzanTagHeader {

            height: 64px;

            display: flex;
            align-items: center;

            padding: 0 18px;

            border-bottom: 1px solid #292d35;

            box-sizing: border-box;
        }


        .slovzanTagBack {

            width: 42px;

            font-size: 30px;

            cursor: pointer;

            user-select: none;
        }


        .slovzanTagTitle {

            flex: 1;

            text-align: center;

            font-size: 19px;

            font-weight: 700;
        }


        .slovzanTagDone {

            width: 42px;

            text-align: right;

            color: #ff3d81;

            font-weight: 700;

            cursor: pointer;
        }


        .slovzanTagSearchArea {

            padding: 14px 16px 8px;
        }


        .slovzanTagSearchBox {

            display: flex;

            align-items: center;

            gap: 8px;

            height: 46px;

            padding: 0 10px;

            background: #20242b;

            border-radius: 12px;

            box-sizing: border-box;
        }


        .slovzanTagSearchBox span {

            font-size: 22px;

            color: #aeb4bd;
        }


        .slovzanTagSearchBox input {

            flex: 1;

            min-width: 0;

            border: 0;
            outline: 0;

            background: transparent;

            color: #fff;

            font-size: 16px;
        }


        .slovzanTagSearchButton {

            border: 0;

            background: #ff3d81;

            color: #fff;

            border-radius: 9px;

            padding: 8px 12px;

            font-weight: 700;

            cursor: pointer;
        }


        .slovzanTagCount {

            padding: 5px 18px 10px;

            color: #aeb4bd;

            font-size: 13px;
        }


        #slovzanTagPeopleResults {

            overflow-y: auto;

            max-height: 55vh;

            padding-bottom: 15px;
        }


        .slovzanTagUser {

            display: flex;

            align-items: center;

            gap: 12px;

            padding: 11px 18px;

            box-sizing: border-box;
        }


        .slovzanTagAvatar {

            width: 48px;
            height: 48px;

            border-radius: 50%;

            object-fit: cover;

            background: #292d35;

            flex-shrink: 0;
        }


        .slovzanTagUsername {

            flex: 1;

            min-width: 0;

            font-size: 16px;

            font-weight: 600;

            overflow: hidden;

            text-overflow: ellipsis;
        }


        .slovzanTagButton {

            border: 0;

            border-radius: 9px;

            padding: 8px 15px;

            background: #ff3d81;

            color: #fff;

            font-weight: 700;

            cursor: pointer;

            flex-shrink: 0;
        }


        .slovzanTagButton.tagged {

            background: #292d35;

            color: #fff;
        }


        .slovzanTagEmpty {

            text-align: center;

            padding: 35px 20px;

            color: #9ba1aa;
        }

        `;

        document.head.appendChild(style);
    }


    /* =====================================================
       HTML ESCAPING
    ===================================================== */

    function escapeHtml(value) {

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    function escapeJs(value) {

        return String(value)
            .replace(/\\/g, "\\\\")
            .replace(/'/g, "\\'");
    }


    /* =====================================================
       COUNT
    ===================================================== */

    function updateCount() {

        const count =
            document.getElementById(
                "slovzanTagCount"
            );

        if (!count) {
            return;
        }

        count.textContent =
            selectedTags.length +
            " / " +
            MAX_TAGS +
            " tagged";
    }


    /* =====================================================
       CREATE MODAL
    ===================================================== */

    function createModal() {

        let modal =
            document.getElementById(
                "slovzanTagPeopleModal"
            );

        if (modal) {
            return modal;
        }


        modal = document.createElement("div");

        modal.id =
            "slovzanTagPeopleModal";


        modal.innerHTML = `

            <div id="slovzanTagPeoplePanel">

                <div class="slovzanTagHeader">

                    <div
                        class="slovzanTagBack"
                        id="slovzanTagBack"
                    >
                        ‹
                    </div>


                    <div class="slovzanTagTitle">
                        Tag people
                    </div>


                    <div
                        class="slovzanTagDone"
                        id="slovzanTagDone"
                    >
                        Done
                    </div>

                </div>


                <div class="slovzanTagSearchArea">

                    <div class="slovzanTagSearchBox">

                        <span>⌕</span>

                        <input
                            id="slovzanTagSearchInput"
                            type="text"
                            placeholder="Search username..."
                            autocomplete="off"
                        >

                        <button
                            type="button"
                            class="slovzanTagSearchButton"
                            id="slovzanTagSearchButton"
                        >
                            Search
                        </button>

                    </div>

                </div>


                <div
                    class="slovzanTagCount"
                    id="slovzanTagCount"
                >
                    0 / 5 tagged
                </div>


                <div id="slovzanTagPeopleResults">

                    <div class="slovzanTagEmpty">
                        Loading...
                    </div>

                </div>

            </div>
        `;


        /* IMPORTANT:
           Direct child of BODY
        */

        document.body.appendChild(modal);


        /* =================================================
           CLOSE ON BACKDROP
        ================================================= */

        modal.addEventListener(
            "click",
            function (e) {

                if (e.target === modal) {
                    closeTagPeople();
                }

            },
            false
        );


        /* =================================================
           BACK
        ================================================= */

        document
            .getElementById("slovzanTagBack")
            .addEventListener(
                "click",
                closeTagPeople
            );


        /* =================================================
           DONE
        ================================================= */

        document
            .getElementById("slovzanTagDone")
            .addEventListener(
                "click",
                closeTagPeople
            );


        /* =================================================
           SEARCH BUTTON
        ================================================= */

        document
            .getElementById("slovzanTagSearchButton")
            .addEventListener(
                "click",
                function () {

                    const input =
                        document.getElementById(
                            "slovzanTagSearchInput"
                        );

                    loadTagPeople(
                        input
                            ? input.value.trim()
                            : ""
                    );
                }
            );


        /* =================================================
           ENTER SEARCH
        ================================================= */

        document
            .getElementById("slovzanTagSearchInput")
            .addEventListener(
                "keydown",
                function (e) {

                    if (e.key === "Enter") {

                        loadTagPeople(
                            this.value.trim()
                        );

                    }

                }
            );


        return modal;
    }


    /* =====================================================
       OPEN
    ===================================================== */

    function openTagPeople() {

        console.log(
            "SLOVZAN OPEN TAG PEOPLE"
        );


        injectStyles();


        const modal =
            createModal();


        if (!modal) {

            console.error(
                "SLOVZAN: MODAL CREATE FAILED"
            );

            return;
        }


        /* FORCE TOP LEVEL */

        if (modal.parentElement !== document.body) {

            document.body.appendChild(
                modal
            );
        }


        modal.style.setProperty(
            "position",
            "fixed",
            "important"
        );

        modal.style.setProperty(
            "top",
            "0",
            "important"
        );

        modal.style.setProperty(
            "left",
            "0",
            "important"
        );

        modal.style.setProperty(
            "right",
            "0",
            "important"
        );

        modal.style.setProperty(
            "bottom",
            "0",
            "important"
        );

        modal.style.setProperty(
            "width",
            "100vw",
            "important"
        );

        modal.style.setProperty(
            "height",
            "100vh",
            "important"
        );

        modal.style.setProperty(
            "z-index",
            "2147483647",
            "important"
        );

        modal.style.setProperty(
            "display",
            "flex",
            "important"
        );


        document.body.style.overflow =
            "hidden";


        updateCount();


        console.log(
            "SLOVZAN TAG MODAL VISIBLE"
        );


        loadTagPeople("");
    }


    /* =====================================================
       CLOSE
    ===================================================== */

    function closeTagPeople() {

        const modal =
            document.getElementById(
                "slovzanTagPeopleModal"
            );

        if (modal) {

            modal.style.setProperty(
                "display",
                "none",
                "important"
            );
        }


        document.body.style.overflow =
            "";
    }


    /* =====================================================
       LOAD USERS
    ===================================================== */

    async function loadTagPeople(query) {

        const results =
            document.getElementById(
                "slovzanTagPeopleResults"
            );

        if (!results) {
            return;
        }


        results.innerHTML = `
            <div class="slovzanTagEmpty">
                Loading...
            </div>
        `;


        try {

            const response =
                await fetch(
                    "/tag_people_users?q=" +
                    encodeURIComponent(
                        query || ""
                    ),
                    {
                        method: "GET",
                        cache: "no-store"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "HTTP " +
                    response.status
                );
            }


            const users =
                await response.json();


            console.log(
                "SLOVZAN TAG USERS =",
                users
            );


            renderUsers(users);

        } catch (error) {

            console.error(
                "SLOVZAN TAG PEOPLE ERROR =",
                error
            );


            results.innerHTML = `
                <div class="slovzanTagEmpty">
                    Unable to load people.
                </div>
            `;
        }
    }


    /* =====================================================
       RENDER USERS
    ===================================================== */

    function renderUsers(users) {

        const results =
            document.getElementById(
                "slovzanTagPeopleResults"
            );

        if (!results) {
            return;
        }


        if (
            !Array.isArray(users) ||
            users.length === 0
        ) {

            results.innerHTML = `
                <div class="slovzanTagEmpty">
                    No mutual followers found.
                </div>
            `;

            return;
        }


        let html = "";


        users.forEach(
            function (user) {

                const username =
                    user.username || "";


                const isTagged =
                    selectedTags.includes(
                        username
                    );


                html += `

                    <div class="slovzanTagUser">

                        <img
                            class="slovzanTagAvatar"
                            src="${escapeHtml(
                                user.profile_pic ||
                                "/static/default.png"
                            )}"
                            onerror="
                                this.src='/static/default.png'
                            "
                        >


                        <div class="slovzanTagUsername">

                            ${escapeHtml(
                                username
                            )}

                        </div>


                        <button
                            type="button"
                            class="slovzanTagButton ${
                                isTagged
                                    ? "tagged"
                                    : ""
                            }"
                            data-username="${escapeHtml(
                                username
                            )}"
                        >
                            ${
                                isTagged
                                    ? "Tagged ✓"
                                    : "Tag"
                            }
                        </button>

                    </div>
                `;
            }
        );


        results.innerHTML =
            html;


        /* BUTTON EVENTS */

        results
            .querySelectorAll(
                ".slovzanTagButton"
            )
            .forEach(
                function (button) {

                    button.addEventListener(
                        "click",
                        function () {

                            toggleTag(
                                this.dataset.username
                            );

                        }
                    );

                }
            );
    }


    /* =====================================================
       TOGGLE TAG
    ===================================================== */

    function toggleTag(username) {

        const index =
            selectedTags.indexOf(
                username
            );


        if (index !== -1) {

            selectedTags.splice(
                index,
                1
            );

        } else {

            if (
                selectedTags.length >=
                MAX_TAGS
            ) {

                alert(
                    "Maximum 5 people can be tagged."
                );

                return;
            }


            selectedTags.push(
                username
            );
        }


        updateCount();


        const input =
            document.getElementById(
                "slovzanTagSearchInput"
            );


        loadTagPeople(
            input
                ? input.value.trim()
                : ""
        );
    }


    /* =====================================================
       UPLOAD API
    ===================================================== */

    window.slovzanGetTaggedPeople =
        function () {

            return selectedTags.slice();
        };


    window.slovzanResetTaggedPeople =
        function () {

            selectedTags = [];

            updateCount();
        };


    /* =====================================================
       GLOBAL OPEN API
    ===================================================== */

    window.slovzanOpenTagPeople =
        function () {

            openTagPeople();
        };


    /* =====================================================
       BUTTON
       Direct + delegated fallback
    ===================================================== */

    function bindTagButton() {

        const button =
            document.getElementById(
                "slovzanTagPeopleButton"
            );


        if (!button) {

            console.error(
                "SLOVZAN TAG PEOPLE BUTTON NOT FOUND"
            );

            return;
        }


        if (
            button.dataset.slovzanTagBound ===
            "1"
        ) {

            return;
        }


        button.dataset.slovzanTagBound =
            "1";


        /* Remove inline onclick so
           only this handler controls it.
        */

        button.removeAttribute(
            "onclick"
        );


        button.addEventListener(
            "click",
            function (e) {

                e.preventDefault();
                e.stopPropagation();

                console.log(
                    "SLOVZAN TAG PEOPLE BUTTON CLICK"
                );


                openTagPeople();

            },
            false
        );


        console.log(
            "SLOVZAN TAG PEOPLE BUTTON READY"
        );
    }


    /* =====================================================
       INITIALIZE
    ===================================================== */

    /* =====================================================
       REEL TAG PEOPLE
       SAME EXISTING TAG PEOPLE MODAL
       POST TAG PEOPLE IS UNTOUCHED
    ===================================================== */

    function bindReelTagButton() {

        const button =
            document.getElementById("reelTagPeopleButton");

        if (!button) {
            return;
        }

        if (button.dataset.slovzanReelTagBound === "1") {
            return;
        }

        button.dataset.slovzanReelTagBound = "1";
        button.removeAttribute("onclick");

        button.addEventListener("click", function (e) {
            e.preventDefault();
            e.stopPropagation();

            console.log("SLOVZAN REEL TAG PEOPLE BUTTON CLICK");

            openTagPeople();
        }, false);

        console.log("SLOVZAN REEL TAG PEOPLE BUTTON READY");
    }


    function initTagPeople() {

        injectStyles();

        createModal();

        bindTagButton();
        bindReelTagButton();


        /* Fallback if Create UI
           gets rendered later.
        */

        setTimeout(
            bindTagButton,
            100
        );
            setTimeout(
                bindReelTagButton,
                100
            );


        setTimeout(
            bindTagButton,
            500
        );
            setTimeout(
                bindReelTagButton,
                500
            );


        setTimeout(
            bindTagButton,
            1000
        );
            setTimeout(
                bindReelTagButton,
                1000
            );

    }


    if (
        document.readyState ===
        "loading"
    ) {

        document.addEventListener(
            "DOMContentLoaded",
            initTagPeople,
            {
                once: true
            }
        );

    } else {

        initTagPeople();
    }


})();

/* TEMP TAG MODAL DEBUG */
setTimeout(function () {
    const modal = document.getElementById("slovzanTagPeopleModal");

    console.log(
        "TAG MODAL DEBUG =",
        modal
            ? modal.style.cssText
            : "MODAL NOT FOUND"
    );
}, 2000);

