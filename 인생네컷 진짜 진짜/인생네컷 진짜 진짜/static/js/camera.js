(async function(){
  const video = document.getElementById('video');
  const captureBtn = document.getElementById('captureBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const countSpan = document.getElementById('count');
  const thumbs = document.getElementById('thumbs');
  const poseOverlay = document.getElementById('poseOverlay');
  const stepText = document.getElementById('stepText');
  const countdownEl = document.getElementById('countdown');

  const stream = await navigator.mediaDevices.getUserMedia({ video: true });
  video.srcObject = stream;

  const captures = [];
  let step = 0;
  let isCounting = false;

  function updatePose(){
    poseOverlay.src = `/static/frames/${SELECTED_FRAME}/pose${step + 1}.png`;
    stepText.textContent = `${step + 1} / 4 촬영`;
  }

  function updateUI(){
    countSpan.textContent = `${captures.length} / 4`;
    thumbs.innerHTML = '';
    captures.forEach(b64 => {
      const img = document.createElement('img');
      img.src = b64;
      img.style.width = '100px';
      img.style.margin = '4px';
      thumbs.appendChild(img);
    });
    uploadBtn.disabled = captures.length !== 4;
  }

  function takePhoto(){
    const c = document.createElement('canvas');
    c.width = video.videoWidth;
    c.height = video.videoHeight;
    c.getContext('2d').drawImage(video, 0, 0);
    captures.push(c.toDataURL('image/jpeg', 0.9));

    step++;
    updateUI();

    if(step < 4){
      updatePose();
    } else {
      poseOverlay.style.display = 'none';
    }
  }

  function startCountdown(){
    if(isCounting || step >= 4) return;
    isCounting = true;

    let count = 0;
    countdownEl.style.display = 'flex';
    countdownEl.textContent = count;

    const timer = setInterval(() => {
      count--;
      if(count > 0){
        countdownEl.textContent = count;
      } else {
        clearInterval(timer);
        countdownEl.style.display = 'none';
        takePhoto();
        isCounting = false;
      }
    }, 1000);
  }

  captureBtn.onclick = startCountdown;

  uploadBtn.onclick = async () => {
    await fetch('/upload', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ images: captures, frame: SELECTED_FRAME })
    });
    location.href = '/result';
  };

  updatePose();
  updateUI();
})();
