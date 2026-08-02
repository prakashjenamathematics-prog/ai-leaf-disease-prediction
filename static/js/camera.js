const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");

function startCamera() {
    navigator.mediaDevices.getUserMedia({ video: true })
        .then(stream => video.srcObject = stream);
}

function capture() {
    const ctx = canvas.getContext("2d");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0);

    canvas.toBlob(blob => {
        const formData = new FormData();
        formData.append("image", blob, "capture.jpg");

        fetch("/predict", {
            method: "POST",
            body: formData
        }).then(() => {
            window.location.href = "/result";
        });
    });
}
