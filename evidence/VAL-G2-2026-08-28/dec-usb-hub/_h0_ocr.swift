import Foundation
import Vision
import AppKit

guard CommandLine.arguments.count >= 2 else {
    fputs("usage: _h0_ocr.swift <image>\n", stderr)
    exit(2)
}
let url = URL(fileURLWithPath: CommandLine.arguments[1])
guard let img = NSImage(contentsOf: url),
      let tiff = img.tiffRepresentation,
      let rep = NSBitmapImageRep(data: tiff),
      let cg = rep.cgImage else {
    fputs("cannot load \(url.path)\n", stderr)
    exit(1)
}
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
let handler = VNImageRequestHandler(cgImage: cg, options: [:])
try handler.perform([req])
let obs = (req.results ?? []).sorted { $0.boundingBox.minY > $1.boundingBox.minY }
for o in obs {
    guard let c = o.topCandidates(1).first else { continue }
    let b = o.boundingBox
    print(String(format: "%.3f\t%.3f\t%.3f\t%.3f\t%.3f\t%@",
                 b.minX, b.minY, b.width, b.height, c.confidence, c.string as NSString))
}
