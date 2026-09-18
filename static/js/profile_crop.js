/* ============================================================
   SLOVZAN PROFILE PHOTO CROP
   Separate Cropper.js module
   ============================================================ */

(function () {
    'use strict';

    let cropper = null;

    function initProfileCrop() {
        const fileInput = document.getElementById('profile-pic-input');
        const imageToCrop = document.getElementById('image-to-crop');
        const cropWrapper = document.getElementById('crop-box-wrapper');
        const hiddenInput = document.getElementById('cropped-image-data');
        const form = document.getElementById('edit-profile-form');

        if (!fileInput || !imageToCrop || !cropWrapper || !hiddenInput || !form) {
            return;
        }

        if (typeof Cropper === 'undefined') {
            console.error('Slovzan Profile Crop: Cropper.js is not loaded.');
            return;
        }

        fileInput.addEventListener('change', function (event) {
            const file = event.target.files && event.target.files[0];

            if (!file || !file.type.startsWith('image/')) {
                return;
            }

            if (cropper) {
                cropper.destroy();
                cropper = null;
            }

            hiddenInput.value = '';

            const reader = new FileReader();

            reader.onload = function (readerEvent) {
                cropWrapper.style.display = 'block';

                imageToCrop.onload = function () {
                    if (cropper) {
                        cropper.destroy();
                    }

                    cropper = new Cropper(imageToCrop, {
                        aspectRatio: 1,
                        viewMode: 1,
                        background: true,
                        autoCropArea: 1,
                        responsive: true,
                        dragMode: 'move',
                        guides: false,
                        center: true,
                        highlight: false,
                        cropBoxMovable: false,
                        cropBoxResizable: false,
                        toggleDragModeOnDblclick: false
                    });

                    // SLOVZAN ROUND PROFILE CROP STYLE
                    const cropperContainer = document.querySelector('.cropper-container');
                    const cropBox = document.querySelector('.cropper-crop-box');
                    const viewBox = document.querySelector('.cropper-view-box');
                    const face = document.querySelector('.cropper-face');

                    if (cropperContainer) {
                        cropperContainer.style.background = '#000';
                    }

                    if (cropBox) {
                        cropBox.style.border = 'none';
                        cropBox.style.outline = 'none';
                        cropBox.style.boxShadow = 'none';
                    }

                    if (viewBox) {
                        viewBox.style.borderRadius = '50%';
                        viewBox.style.border = 'none';
                        viewBox.style.outline = 'none';
                        viewBox.style.boxShadow = 'none';
                        viewBox.style.overflow = 'hidden';
                    }

                    if (face) {
                        face.style.background = 'transparent';
                        face.style.backgroundColor = 'transparent';
                        face.style.opacity = '0';
                        face.style.border = 'none';
                        face.style.outline = 'none';
                    }
                };

                imageToCrop.src = readerEvent.target.result;
            };

            reader.readAsDataURL(file);
        });

        form.addEventListener('submit', function () {
            if (!cropper) {
                return;
            }

            const canvas = cropper.getCroppedCanvas({
                width: 400,
                height: 400,
                imageSmoothingEnabled: true,
                imageSmoothingQuality: 'high'
            });

            if (canvas) {
                hiddenInput.value = canvas.toDataURL('image/jpeg', 0.92);
            }
        });
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initProfileCrop);
    } else {
        initProfileCrop();
    }

    window.slovzanProfileCropDestroy = function () {
        if (cropper) {
            cropper.destroy();
            cropper = null;
        }
    };
})();
