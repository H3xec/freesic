import Foundation

struct Track: Identifiable, Decodable {
    let id: String
    let title: String
    let duration: Int?
    let thumbnail: String?
    let uploader: String?
}

struct SearchResponse: Decodable {
    let results: [Track]
}

struct StreamResponse: Decodable {
    let id: String
    let title: String
    let duration: Int?
    let audio_url: String
    let thumbnail: String?
}
