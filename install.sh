# required
sudo apt install \
  build-essential \
  python3 \
  python3-dev \
  python3-pip \
  python-is-python3 \
  python3.10-venv \
  portaudio19-dev \
  python3-pyaudio \
  libespeak1 \
  espeak \
  -y

# groups 에 audio 그룹이 없다면 오디오 그룹에 추가되어야 함
if [ $(getent group audio) ]; then
  echo "audio group exists"
else
  sudo usermod -aG audio $USER
fi

# optional
sudo apt install \
  alsa-utils \
  -y

# required
pip install \
  openai \
  python-dotenv \
  speechrecognition \
  pyttsx3 \
  numpy \
  pyaudio