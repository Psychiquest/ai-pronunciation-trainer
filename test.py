import base64
import ffmpeg

ffmpeg.input("https://storage.googleapis.com/kagglesdsdata/datasets/829978/1417968/harvard.wav?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Credential=databundle-worker-v2%40kaggle-161607.iam.gserviceaccount.com%2F20241008%2Fauto%2Fstorage%2Fgoog4_request&X-Goog-Date=20241008T024112Z&X-Goog-Expires=345600&X-Goog-SignedHeaders=host&X-Goog-Signature=56630c2b4e257bc18dc82dc574747473c2c044bbf46d7615447ef016cc38e08a14aa5b57c63abfb54c36023569698d7dcd451b64ad212f9d870020ad155c81014ba010ef1a89a6ca75764518fa8b8817cdf4e20476b2b3497b895518c4b2418892cb33e7a05c7651f8516a0b7a482a0297fdb52dd03a7edfdb4738a5191d9d1d0efa5351a73ae0157fdf25c7a5c463d38e525cfae1d536f5b4d730a9edcc98840e839026917f97a1faa284524e4dbf87a2a7c1afc3679e85423621985939ec9f2c4d581c97ba01ba9494178a55c8c5a4b61658502b6c4042e61b6707fb7cd489414f15747cfa2269ff40bc3baf150a691081ab75e22b5cc194300861b44f7abf").output("a_converted.wav", ac=1, ar=48000).run()

# Function to encode audio file to base64
def encode_audio(file_path):
    with open(file_path, "rb") as audio_file:
        return base64.b64encode(audio_file.read()).decode('utf-8')

        
audio_base64 = encode_audio("a_converted.wav")
print(audio_base64)