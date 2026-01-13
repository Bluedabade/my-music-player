import streamlit as st

# --- Song Class (Updated to hold file data) ---
class Song:
    def __init__(self, title, artist, file_data):
        self.title = title
        self.artist = artist
        self.file_data = file_data  # เก็บข้อมูลไฟล์เพลง
        self.next_song = None

    def __str__(self):
        return f"{self.title} by {self.artist}"

# --- MusicPlaylist Class ---
class MusicPlaylist:
    def __init__(self):
        self.head = None
        self.current_song = None
        self.length = 0

    def add_song(self, title, artist, file_data):
        new_song = Song(title, artist, file_data)
        if self.head is None:
            self.head = new_song
            self.current_song = new_song
        else:
            current = self.head
            while current.next_song:
                current = current.next_song
            current.next_song = new_song
        self.length += 1
        st.success(f"Added: {new_song}")

    def display_playlist(self):
        if self.head is None:
            return []

        playlist_songs = []
        current = self.head
        count = 1
        while current:
            # Mark the current song with a symbol
            prefix = "▶️ " if current == self.current_song else "   "
            playlist_songs.append(f"{prefix}{count}. {current.title} by {current.artist}")
            current = current.next_song
            count += 1
        return playlist_songs

    def get_current_song_data(self):
        """คืนค่าข้อมูลเพลงปัจจุบันเพื่อนำไปเล่น"""
        return self.current_song

    def next_song(self):
        if self.current_song and self.current_song.next_song:
            self.current_song = self.current_song.next_song
        elif self.current_song and not self.current_song.next_song:
            st.warning("End of playlist. No next song.")
        else:
            st.warning("Playlist is empty.")

    def prev_song(self):
        if self.head is None or self.current_song is None:
            st.warning("Playlist is empty or no song is selected.")
            return
        if self.current_song == self.head:
            st.warning("Already at the beginning of the playlist.")
            return

        current = self.head
        while current.next_song != self.current_song:
            current = current.next_song
        self.current_song = current

    def get_length(self):
        return self.length

    def delete_song(self, title):
        if self.head is None:
            st.error(f"Cannot delete '{title}'. Playlist is empty.")
            return

        # If the song to be deleted is the head
        if self.head.title == title:
            if self.current_song == self.head:
                self.current_song = self.head.next_song
            self.head = self.head.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
            if self.length == 0:
                self.current_song = None
            return

        current = self.head
        prev = None
        while current and current.title != title:
            prev = current
            current = current.next_song

        if current:
            if self.current_song == current:
                if current.next_song:
                    self.current_song = current.next_song
                elif prev:
                    self.current_song = prev
                else:
                    self.current_song = None

            prev.next_song = current.next_song
            self.length -= 1
            st.success(f"Deleted: {title}")
        else:
            st.error(f"Song '{title}' not found in the playlist.")

# --- Streamlit App Layout ---
st.title("🎶 Music Playlist App (With Player)")

# Initialize playlist in session state
if 'playlist' not in st.session_state:
    st.session_state.playlist = MusicPlaylist()

# Sidebar for adding songs
st.sidebar.header("Add New Song")
uploaded_file = st.sidebar.file_uploader("Upload MP3/WAV file", type=['mp3', 'wav', 'ogg'])
new_title = st.sidebar.text_input("Title")
new_artist = st.sidebar.text_input("Artist")

if st.sidebar.button("Add Song to Playlist"):
    if uploaded_file and new_title and new_artist:
        # ส่งไฟล์ที่อัปโหลด (uploaded_file) ไปเก็บใน Linked List ด้วย
        st.session_state.playlist.add_song(new_title, new_artist, uploaded_file)
    elif not uploaded_file:
        st.sidebar.warning("Please upload an audio file.")
    else:
        st.sidebar.warning("Please enter both title and artist.")

st.sidebar.markdown("--- 🎶")
st.sidebar.header("Delete Song")
delete_title = st.sidebar.text_input("Song Title to Delete")
if st.sidebar.button("Delete Song"):
    if delete_title:
        st.session_state.playlist.delete_song(delete_title)
        # Force rerun to update UI immediately
        st.rerun() 
    else:
        st.sidebar.warning("Please enter a song title to delete.")

# Main content
st.header("Your Current Playlist")
playlist_content = st.session_state.playlist.display_playlist()
if playlist_content:
    for song_str in playlist_content:
        st.text(song_str) # Use text to preserve spacing
else:
    st.info("Playlist is empty. Add some songs from the sidebar!")

st.markdown("---")

# --- Player Section ---
st.header("🎧 Now Playing")

# ดึงข้อมูลเพลงปัจจุบันมาแสดง
current_track = st.session_state.playlist.get_current_song_data()

if current_track:
    st.subheader(f"{current_track.title} - {current_track.artist}")
    
    # แสดงเครื่องเล่นเพลง (Audio Player)
    # เราใช้ uploaded_file ที่เก็บไว้ใน node มาเล่น
    st.audio(current_track.file_data, format='audio/mp3')
else:
    st.write("No song selected.")

st.markdown("---")

# --- Controls ---
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    if st.button("⏪ Previous Song", use_container_width=True):
        st.session_state.playlist.prev_song()
        st.rerun() # Rerun to update the player immediately

with col2:
    # ปุ่ม Refresh เฉยๆ ในกรณีที่ Player ค้าง (จริงๆ st.audio ทำงาน auto อยู่แล้ว)
    st.button("🔄 Refresh Player", use_container_width=True)

with col3:
    if st.button("Next Song ⏩", use_container_width=True):
        st.session_state.playlist.next_song()
        st.rerun() # Rerun to update the player immediately

st.markdown("---")
st.caption(f"Total songs in playlist: {st.session_state.playlist.get_length()} song(s)")
