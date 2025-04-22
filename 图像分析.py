import os
import cv2
import numpy as np
import pandas as pd
from itertools import combinations

def match_images(img_path1, img_path2, output_path="matches.jpg", min_match_count=10):
    img1 = cv2.imread(img_path1, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(img_path2, cv2.IMREAD_GRAYSCALE)

    orb = cv2.ORB_create(nfeatures=1000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return None

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)

    matched_img = cv2.drawMatches(img1, kp1, img2, kp2, matches[:min_match_count], None, flags=2)
    cv2.imwrite(output_path, matched_img)

    score = len(matches) / min(len(kp1), len(kp2))

    return {
        "Image1": os.path.basename(img_path1),
        "Image2": os.path.basename(img_path2),
        "MatchCount": len(matches),
        "Keypoints1": len(kp1),
        "Keypoints2": len(kp2),
        "Score": round(score, 4),
        "Output": os.path.basename(output_path)
    }

def batch_compare_images(input_dir, output_dir, csv_path="match_summary.csv"):
    os.makedirs(output_dir, exist_ok=True)

    image_files = [f for f in os.listdir(input_dir) if f.lower().endswith((".tif", ".tiff", ".png", ".jpg", ".jpeg"))]
    pairs = combinations(image_files, 2)

    results = []

    for img1, img2 in pairs:
        path1 = os.path.join(input_dir, img1)
        path2 = os.path.join(input_dir, img2)
        out_name = f"{os.path.splitext(img1)[0]}__vs__{os.path.splitext(img2)[0]}.jpg"
        out_path = os.path.join(output_dir, out_name)

        print(f"Comparing {img1} vs {img2}...")
        result = match_images(path1, path2, output_path=out_path)
        if result:
            results.append(result)

    df = pd.DataFrame(results)
    df.to_csv(os.path.join(output_dir, csv_path), index=False)
    print(f"\n✅ 所有比对完成，结果已保存至：{output_dir}/{csv_path}")


batch_compare_images(
    "/Users/wangyong/Library/Containers/com.tencent.xinWeChat/Data/Library/Application Support/com.tencent.xinWeChat/2.0b4.0.9/a97fa5db58356f4748f2bdcc63f23e66/Message/MessageTemp/a78dd168d9d5fef324ed2b134732ec42/File/统计/免疫组化/",
    "/Users/wangyong/Desktop/output")
