import Foundation
import AVFoundation
import MediaPlayer
import UIKit

/// Gère la lecture audio, y compris écran éteint / app en arrière-plan.
final class PlayerManager: ObservableObject {
    static let shared = PlayerManager()

    private var player: AVPlayer?
    @Published var isPlaying = false
    @Published var currentTrackTitle: String = ""

    private init() {
        configureAudioSession()
    }

    private func configureAudioSession() {
        do {
            let session = AVAudioSession.sharedInstance()
            // .playback permet la lecture même écran verrouillé / app en fond
            try session.setCategory(.playback, mode: .default, options: [])
            try session.setActive(true)
        } catch {
            print("Erreur config AVAudioSession: \(error)")
        }
    }

    func play(track: StreamResponse) {
        guard let url = URL(string: track.audio_url) else { return }

        let item = AVPlayerItem(url: url)
        player = AVPlayer(playerItem: item)
        player?.play()
        isPlaying = true
        currentTrackTitle = track.title

        setupNowPlaying(title: track.title, artworkURL: track.thumbnail, duration: track.duration)
        setupRemoteCommands()
    }

    func pause() {
        player?.pause()
        isPlaying = false
    }

    func resume() {
        player?.play()
        isPlaying = true
    }

    func togglePlayPause() {
        isPlaying ? pause() : resume()
    }

    // Affiche les infos sur l'écran verrouillé + centre de contrôle
    private func setupNowPlaying(title: String, artworkURL: String?, duration: Int?) {
        var info: [String: Any] = [
            MPMediaItemPropertyTitle: title,
        ]
        if let duration = duration {
            info[MPMediaItemPropertyPlaybackDuration] = Double(duration)
        }
        MPNowPlayingInfoCenter.default().nowPlayingInfo = info

        // Chargement asynchrone de l'artwork (optionnel)
        if let artworkURL = artworkURL, let url = URL(string: artworkURL) {
            URLSession.shared.dataTask(with: url) { data, _, _ in
                guard let data = data, let image = UIImage(data: data) else { return }
                let artwork = MPMediaItemArtwork(boundsSize: image.size) { _ in image }
                DispatchQueue.main.async {
                    var current = MPNowPlayingInfoCenter.default().nowPlayingInfo ?? [:]
                    current[MPMediaItemPropertyArtwork] = artwork
                    MPNowPlayingInfoCenter.default().nowPlayingInfo = current
                }
            }.resume()
        }
    }

    // Permet de contrôler la lecture depuis l'écran verrouillé / écouteurs
    private func setupRemoteCommands() {
        let commandCenter = MPRemoteCommandCenter.shared()

        commandCenter.playCommand.removeTarget(nil)
        commandCenter.playCommand.addTarget { [weak self] _ in
            self?.resume()
            return .success
        }

        commandCenter.pauseCommand.removeTarget(nil)
        commandCenter.pauseCommand.addTarget { [weak self] _ in
            self?.pause()
            return .success
        }

        commandCenter.togglePlayPauseCommand.removeTarget(nil)
        commandCenter.togglePlayPauseCommand.addTarget { [weak self] _ in
            self?.togglePlayPause()
            return .success
        }
    }
}
