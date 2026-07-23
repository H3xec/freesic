import SwiftUI

// ⚠️ Remplace par l'adresse IP locale de ton Mac (ipconfig getifaddr en0)
// tant que le backend tourne en local sur le même wifi.
let BACKEND_URL = "https://freesic-backend.onrender.com"

struct ContentView: View {
    @State private var query = ""
    @State private var results: [Track] = []
    @State private var isLoading = false
    @StateObject private var player = PlayerManager.shared

    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                searchBar

                if isLoading {
                    ProgressView().padding()
                }

                List(results) { track in
                    Button {
                        Task { await playTrack(track) }
                    } label: {
                        VStack(alignment: .leading) {
                            Text(track.title).font(.body).lineLimit(2)
                            if let uploader = track.uploader {
                                Text(uploader).font(.caption).foregroundColor(.secondary)
                            }
                        }
                    }
                }
                .listStyle(.plain)

                nowPlayingBar
            }
            .navigationTitle("YTMusic")
        }
    }

    private var searchBar: some View {
        HStack {
            TextField("Rechercher un titre, un artiste...", text: $query)
                .textFieldStyle(.roundedBorder)
                .onSubmit { Task { await search() } }
            Button("Go") { Task { await search() } }
        }
        .padding()
    }

    private var nowPlayingBar: some View {
        Group {
            if !player.currentTrackTitle.isEmpty {
                HStack {
                    Text(player.currentTrackTitle)
                        .lineLimit(1)
                    Spacer()
                    Button {
                        player.togglePlayPause()
                    } label: {
                        Image(systemName: player.isPlaying ? "pause.fill" : "play.fill")
                    }
                }
                .padding()
                .background(.thinMaterial)
            }
        }
    }

    private func search() async {
        guard !query.isEmpty else { return }
        isLoading = true
        defer { isLoading = false }

        guard let url = URL(string: "\(BACKEND_URL)/search?q=\(query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")") else { return }

        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let decoded = try JSONDecoder().decode(SearchResponse.self, from: data)
            results = decoded.results
        } catch {
            print("Erreur recherche: \(error)")
        }
    }

    private func playTrack(_ track: Track) async {
        guard let url = URL(string: "\(BACKEND_URL)/stream?id=\(track.id)") else { return }
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let stream = try JSONDecoder().decode(StreamResponse.self, from: data)
            player.play(track: stream)
        } catch {
            print("Erreur lecture: \(error)")
        }
    }
}
