(async function(){
  const video = document.getElementById('video');
  const captureBtn = document.getElementById('captureBtn');
  const uploadBtn = document.getElementById('uploadBtn');
  const countSpan = document.getElementById('count');
  const thumbs = document.getElementById('thumbs');

  let stream = null;
  try{
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    video.srcObject = stream;
  }catch(err){
    alert('카메라 접근 실패: ' + err.message);
    return;
  }

  const captures = [];

  function updateUI(){
    countSpan.textContent = `${captures.length} / 4`;
    thumbs.innerHTML = '';
    captures.forEach((b64, idx) => {
      const img = document.createElement('img');
      img.src = b64;
      img.style.width = '120px';
      img.style.margin = '4px';
      thumbs.appendChild(img);
    });
    uploadBtn.disabled = captures.length !== 4;
  }

  captureBtn.addEventListener('click', ()=>{
    if(captures.length >= 4) return;
    const w = video.videoWidth;
    const h = video.videoHeight;
    const canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, w, h);
    const data = canvas.toDataURL('image/jpeg', 0.9);
    captures.push(data);
    updateUI();
  });

  uploadBtn.addEventListener('click', async ()=>{
    if(captures.length !== 4) return;
    uploadBtn.textContent = '업로드 중...';
    uploadBtn.disabled = true;
    try{
      const res = await fetch('/upload', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ images: captures, frame: SELECTED_FRAME })
      });
      const j = await res.json();
      if(j.result_url){
        window.location.href = '/result';
      }else{
        alert('서버 에러');
      }
    }catch(e){
      alert('업로드 실패: '+ e.message);
    }finally{
      uploadBtn.textContent = '업로드 및 합성';
      uploadBtn.disabled = false;
    }
  });

  updateUI();
})();
