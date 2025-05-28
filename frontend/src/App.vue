<template>
  <div class="camera-app-container">
    <h1>Webcam Access with Vue.js</h1>

    <div v-if="errorMessage" class="error-message">
      <p>Error: {{ errorMessage }}</p>
      <p>Please check your browser permissions or ensure a camera is available.</p>
    </div>

    <div v-else class="video-wrapper">
      <video ref="videoElement" autoplay muted playsinline></video>
      <button @click="takePhoto" :disabled="!isCameraReady" class="take-photo-button">
        Tirar Foto
      </button>
    </div>

    <div v-show="photoTaken" class="photo-preview">
      <h2>Foto Capturada:</h2>
      <canvas ref="photoCanvas"></canvas>
      <a :href="photoDataURL" download="minha-foto.png" class="download-button">
        Baixar Foto
      </a>
      <button @click="clearPhoto" class="clear-photo-button">
        Tirar Outra
      </button>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'CameraApp', // Nome do seu componente

  setup() {
    const videoElement = ref(null); // Ref para o elemento <video>
    const photoCanvas = ref(null);  // Ref para o elemento <canvas>
    let currentStream = null;      // Armazena o MediaStream da câmera

    const errorMessage = ref('');  // Mensagens de erro para o usuário
    const isCameraReady = ref(false); // Indica se a câmera está pronta
    const photoTaken = ref(false);   // Indica se uma foto foi tirada
    const photoDataURL = ref('');    // URL da foto capturada

    // Função para iniciar a câmera
    const startCamera = async () => {
      errorMessage.value = ''; // Limpa mensagens de erro anteriores
      isCameraReady.value = false;
      photoTaken.value = false;
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
    const takePhoto = () => {
      if (!isCameraReady.value || !videoElement.value) {
        errorMessage.value = 'A câmera não está pronta para tirar a foto.';
        return;
      }

      const video = videoElement.value;
      const canvas = photoCanvas.value;
      const context = canvas.getContext('2d');

      // Ajustar o tamanho do canvas para o tamanho atual do vídeo
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Desenhar o frame atual do vídeo no canvas
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      const data = {
        image: canvas.toDataURL('image/png')
      }
      fetch('https://localhost:5000', {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            })
            .then(data => {console.log(data.json())})
      // Converter o conteúdo do canvas para uma imagem URL
      photoDataURL.value = canvas.toDataURL('image/png'); // 'image/jpeg' é outra opção
      photoTaken.value = true;
      console.log('Foto capturada!');
    };

    // Limpar a foto capturada e voltar ao vídeo
    const clearPhoto = () => {
      photoTaken.value = false;
      photoDataURL.value = '';
    };

    // Hooks de ciclo de vida do Vue
    onMounted(() => {
      startCamera(); // Inicia a câmera quando o componente é montado
    });

    onBeforeUnmount(() => {
      stopCamera(); // Para a câmera quando o componente é desmontado
    });

    // Retorna as variáveis e funções para serem usadas no template
    return {
      videoElement,
      photoCanvas,
      errorMessage,
      isCameraReady,
      photoTaken,
      photoDataURL,
      takePhoto,
      clearPhoto
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

.photo-preview {
  margin-top: 30px;
  text-align: center;
  background-color: #ffffff;
  padding: 25px;
  border-radius: 10px;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
  max-width: 600px;
  width: 100%;
}

.photo-preview h2 {
  color: #34495e;
  margin-bottom: 20px;
}

canvas {
  max-width: 100%;
  height: auto;
  border: 2px solid #555;
  border-radius: 8px;
  display: block;
  margin: 0 auto 20px auto; /* Centraliza e adiciona margem inferior */
}

.download-button,
.clear-photo-button {
  display: inline-block;
  padding: 10px 20px;
  font-size: 1em;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  margin: 0 10px;
  transition: background-color 0.3s ease;
}

.download-button {
  background-color: #007bff;
  color: white;
  text-decoration: none; /* Para o link */
}

.download-button:hover {
  background-color: #0056b3;
}

.clear-photo-button {
  background-color: #6c757d;
  color: white;
}

.clear-photo-button:hover {
  background-color: #5a6268;
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
  .photo-preview {
    padding: 15px;
  }
  .download-button,
  .clear-photo-button {
    font-size: 0.9em;
    padding: 8px 15px;
    margin: 5px;
  }
}
</style>