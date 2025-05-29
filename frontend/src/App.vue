<template>
  <div class="camera-app-container">
    <h1>Scaneie o QRcode</h1>
    <button @click="startCamera" class="take-photo-button">Tirar Foto</button>

    <div v-if="errorMessage" class="error-message">
      <p>Error: {{ errorMessage }}</p>
      <p>Please check your browser permissions or ensure a camera is available.</p>
    </div>

    <div v-else class="video-wrapper" v-show="scan">
      <video ref="videoElement" autoplay muted playsinline></video>
    </div>
      <canvas ref="photoCanvas" style="display: none"></canvas>
  </div>
</template>

<script>
import { ref, onBeforeUnmount } from 'vue';

export default {
  name: 'CameraApp', // Nome do seu componente

  setup() {
    const videoElement = ref(null); // Ref para o elemento <video>
    const photoCanvas = ref(null);  // Ref para o elemento <canvas>
    let currentStream = null;      // Armazena o MediaStream da câmera

    const errorMessage = ref('');  // Mensagens de erro para o usuário
    const isCameraReady = ref(false); // Indica se a câmera está pronta
    const photoDataURL = ref('');    // URL da foto capturada
    const scan = ref(false)

    // Função para iniciar a câmera
    const startCamera = async () => {
      scan.value = true
      errorMessage.value = ''; // Limpa mensagens de erro anteriores
      isCameraReady.value = false;
      photoDataURL.value = '';

      const constraints = {
        video: {
          facingMode: 'environment', // 'user' para câmera frontal, 'environment' para traseira
          width: { ideal: 1280 }, // Resolução ideal
          height: { ideal: 720 }
        },
        audio: false
      };

      try {
        currentStream = await navigator.mediaDevices.getUserMedia(constraints);
        videoElement.value.srcObject = currentStream;
        videoElement.value.onloadedmetadata = () => {
          videoElement.value.play(); // Garantir que o vídeo comece a tocar
          isCameraReady.value = true;
          takePhoto()
          console.log('Câmera carregada e vídeo pronto!');
        };

      } catch (err) {
        console.error('Erro ao acessar a câmera:', err);
        if (err.name === 'NotAllowedError') {
          errorMessage.value = 'Permissão da câmera negada.';
        } else if (err.name === 'NotFoundError') {
          errorMessage.value = 'Nenhuma câmera encontrada.';
        } else {
          errorMessage.value = `Ocorreu um erro: ${err.message || err.name}`;
        }
      }
    };

    // Função para parar a câmera
    const stopCamera = () => {
      if (currentStream) {
        currentStream.getTracks().forEach(track => {
          track.stop(); // Para cada trilha (vídeo, áudio), pare-a
        });
        currentStream = null;
        console.log('Câmera parada.');
      }
    };


    // Função para tirar uma foto
    async function takePhoto(){
      if (!isCameraReady.value || !videoElement.value) {
        errorMessage.value = 'A câmera não está pronta para tirar a foto.';
        return;
      }

      const canvas = photoCanvas.value;
      const context = canvas.getContext('2d');
      let video = videoElement.value;
      
      // Ajustar o tamanho do canvas para o tamanho atual do vídeo
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      const data = {
        image: canvas.toDataURL('image/png')
      }
      let c = 0
      let attempts = 0
      const inicio = Date.now()
      while (c < 1 && attempts < 50 && (Date.now() - inicio) < 15000) {
        video = videoElement.value
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        data.image = canvas.toDataURL('image/png')

        const response = await fetch('https://400e-2804-d59-f727-8b00-4c48-e729-b9a4-8713.ngrok-free.app/', {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(data)
        })
        const responseconv = await response.json()
        if (responseconv.status == 200) {
          c = 1
        }
        attempts++
      }
      if (c === 0) {
        errorMessage.value = "Não foi possível escanear o QRcode. Tente novamente"
      }
      scan.value = false
      // Converter o conteúdo do canvas para uma imagem URL
    }

    onBeforeUnmount(() => {
      stopCamera(); // Para a câmera quando o componente é desmontado
    });

    // Retorna as variáveis e funções para serem usadas no template
    return {
      videoElement,
      photoCanvas,
      errorMessage,
      isCameraReady,
      photoDataURL,
      takePhoto,
      startCamera,
      scan
    };
  }
};
</script>

<style scoped>
/* O atributo 'scoped' limita o CSS a este componente */
.camera-app-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  padding: 20px;
  box-sizing: border-box;
  font-family: 'Arial', sans-serif;
  background-color: #f4f7f6;
  color: #333;
}

h1 {
  color: #2c3e50;
  margin-bottom: 30px;
}

.error-message {
  color: #e74c3c;
  background-color: #fdeded;
  border: 1px solid #e74c3c;
  padding: 15px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
  max-width: 600px;
  width: 100%;
}

.video-wrapper {
  position: relative;
  width: 100%;
  max-width: 600px; /* Limite para telas maiores */
  border: 4px solid #3498db;
  border-radius: 10px;
  overflow: hidden; /* Garante que o vídeo não "estoure" a borda */
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  margin-bottom: 30px;
}

video {
  width: 100%;
  height: auto;
  display: block; /* Remove espaços extras abaixo do vídeo */
  background-color: black;
}

.take-photo-button {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 25px;
  font-size: 1.1em;
  background-color: #28a745;
  color: white;
  border: none;
  border-radius: 30px; /* Botão redondo */
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
  transition: background-color 0.3s ease, transform 0.2s ease;
  white-space: nowrap; /* Evita que o texto quebre */
}

.take-photo-button:hover:not(:disabled) {
  background-color: #218838;
  transform: translateX(-50%) scale(1.05);
}

.take-photo-button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
  opacity: 0.7;
}


/* Responsividade básica */
@media (max-width: 768px) {
  .camera-app-container {
    padding: 15px;
  }
  h1 {
    font-size: 1.8em;
  }
  .take-photo-button {
    font-size: 1em;
    padding: 10px 20px;
  }
}
</style>