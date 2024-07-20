clipdrop_key = 'c3e3e0e0-3e3e-11ec-8e0e-3e3e0e3e3e0e'
clipdrop_key = 'af3a5106fcabe75849a6b2210c22c8faf0555826b2587a2e4dd363eaa8f66b6b181cb4e2ab77c82edfc302bca0e320c7'


from PIL import Image



trashcan_image = Image.open('temp/trashcan_image_bol.jpg')



# remove white background from trashcan_image
image = trashcan_image
image = image.convert("RGBA")
image_data = image.getdata()
print(image_data)
new_data = []
for item in image_data:
    item0 = item[0]
    if item[0] in list(range(240, 256)):
        new_data.append((255, 255, 255, 0))
    else:
        new_data.append(item)
image.putdata(new_data)
trashcan_image = image

trashcan_image.save('temp/trashcan_image_rembg.png')



# import torch
# from carvekit.api.high import HiInterface

# # Check doc strings for more information
# interface = HiInterface(object_type="hairs-like",  # Can be "object" or "hairs-like".
#                         batch_size_seg=5,
#                         batch_size_matting=1,
#                         device='cuda' if torch.cuda.is_available() else 'cpu',
#                         seg_mask_size=640,  # Use 640 for Tracer B7 and 320 for U2Net
#                         matting_mask_size=2048,
#                         trimap_prob_threshold=231,
#                         trimap_dilation=30,
#                         trimap_erosion_iters=5,
#                         fp16=False)
# images_without_background = interface(['./temp/trashcan_image_bol.jpg'])
# cat_wo_bg = images_without_background[0]
# cat_wo_bg.save('trashcan_rembg.png')

                   