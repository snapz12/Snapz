/* =====================================================
   SLOVZAN REELS TAG PEOPLE (ISOLATED)
===================================================== */
(function() {
    console.log("Loading isolated Reel Tagging...");

    window.slovzanOpenReelTagPeople = function() {
        console.log("Reel Tag Modal Opened!");
        
        let modal = document.getElementById("slovzanReelTagModal");
        if (!modal) {
            modal = document.createElement("div");
            modal.id = "slovzanReelTagModal";
            modal.style.cssText = "position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:999999;display:flex;align-items:center;justify-content:center;";
            modal.innerHTML = `
                <div style="background:#1e1e1e;color:#fff;width:90%;max-width:400px;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.5);">
                    <div style="display:flex;justify-content:space-between;align-items:center;padding:14px 16px;border-bottom:1px solid #333;">
                        <h3 style="margin:0;font-size:16px;font-weight:600;">Tag People (Reels)</h3>
                        <button type="button" id="slovzanReelCloseModal" style="background:none;border:none;color:#aaa;font-size:20px;cursor:pointer;">&times;</button>
                    </div>
                    <div style="padding:12px;">
                        <input type="text" id="slovzanReelSearchInput" placeholder="Search users..." style="width:100%;padding:10px 12px;background:#2a2a2a;border:1px solid #444;color:#fff;border-radius:6px;box-sizing:border-box;font-size:14px;outline:none;">
                    </div>
                    <div id="slovzanReelUserList" style="max-height:250px;overflow-y:auto;padding:0 16px 16px;">
                        <p style="text-align:center;color:#888;font-size:14px;">Type to search users...</p>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);

            document.getElementById("slovzanReelCloseModal").onclick = () => { modal.style.display = "none"; };
            modal.onclick = (e) => { if (e.target === modal) modal.style.display = "none"; };

            document.getElementById("slovzanReelSearchInput").oninput = function() {
                const query = this.value.trim();
                const container = document.getElementById("slovzanReelUserList");
                
                if (!query) {
                    container.innerHTML = '<p style="text-align:center;color:#888;font-size:14px;">Type to search users...</p>';
                    return;
                }

                fetch(`/tag_people_users?q=${encodeURIComponent(query)}`)
                    .then(res => res.json())
                    .then(data => {
                        if (!data || data.length === 0) {
                            container.innerHTML = '<p style="text-align:center;color:#888;font-size:14px;">No users found</p>';
                            return;
                        }
                        let html = "";
                        data.forEach(user => {
                            html += `
                                <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid #333;">
                                    <div style="display:flex;align-items:center;gap:10px;">
                                        <img src="${user.profile_pic || '/static/default_profile.png'}" style="width:32px;height:32px;border-radius:50%;object-fit:cover;">
                                        <span style="font-weight:600;font-size:14px;">${user.username}</span>
                                    </div>
                                    <button type="button" onclick="alert('Tagged ${user.username}')" style="background:#0095f6;color:white;border:none;padding:4px 12px;border-radius:4px;font-weight:600;font-size:12px;cursor:pointer;">Tag</button>
                                </div>
                            `;
                        });
                        container.innerHTML = html;
                    })
                    .catch(() => {
                        container.innerHTML = '<p style="text-align:center;color:red;font-size:14px;">Error fetching users</p>';
                    });
            };
        }

        modal.style.display = "flex";
    };

    // Universal delegation specifically for the Reel tag button
    document.addEventListener("click", function(e) {
        const btn = e.target.closest("#slovzanReelTagPeopleButton");
        if (btn) {
            e.preventDefault();
            e.stopPropagation();
            window.slovzanOpenReelTagPeople();
        }
    }, true);
})();
