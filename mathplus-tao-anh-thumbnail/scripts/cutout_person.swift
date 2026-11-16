import Foundation
import CoreGraphics
import CoreImage
import Vision
import AppKit

guard CommandLine.arguments.count >= 3 else {
    print("Usage: swift cutout_person.swift <input_path> <output_path>")
    exit(1)
}

let inputPath = CommandLine.arguments[1]
let outputPath = CommandLine.arguments[2]

guard let inputImage = NSImage(contentsOfFile: inputPath),
      let tiffData = inputImage.tiffRepresentation,
      let bitmap = NSBitmapImageRep(data: tiffData),
      let cgImage = bitmap.cgImage else {
    print("Error: Cannot load image at \(inputPath)")
    exit(1)
}

let request = VNGeneratePersonSegmentationRequest()
request.qualityLevel = .accurate
request.outputPixelFormat = kCVPixelFormatType_OneComponent8

let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])
do {
    try handler.perform([request])
    guard let result = request.results?.first else {
        print("Error: No person segmentation result")
        exit(1)
    }
    
    let maskPixelBuffer = result.pixelBuffer
    let ciMask = CIImage(cvPixelBuffer: maskPixelBuffer)
    let ciInput = CIImage(cgImage: cgImage)
    
    // Scale mask to match input dimensions
    let scaleX = CGFloat(cgImage.width) / CGFloat(CVPixelBufferGetWidth(maskPixelBuffer))
    let scaleY = CGFloat(cgImage.height) / CGFloat(CVPixelBufferGetHeight(maskPixelBuffer))
    let scaledMask = ciMask.transformed(by: CGAffineTransform(scaleX: scaleX, y: scaleY))
    
    // Save mask as grayscale png
    let context = CIContext(options: nil)
    guard let maskCG = context.createCGImage(scaledMask, from: CGRect(x: 0, y: 0, width: cgImage.width, height: cgImage.height)) else {
        print("Error: Cannot create mask CGImage")
        exit(1)
    }
    
    let rep = NSBitmapImageRep(cgImage: maskCG)
    guard let pngData = rep.representation(using: .png, properties: [:]) else {
        print("Error: Cannot convert mask to PNG")
        exit(1)
    }
    
    let tempMaskPath = outputPath + ".mask.png"
    try pngData.write(to: URL(fileURLWithPath: tempMaskPath))
    print("SUCCESS: Mask saved to \(tempMaskPath)")
} catch {
    print("Error: \(error)")
    exit(1)
}
