import sys
import os
import re

# Function to convert to SRT format
def convertcontent(vttcontent):

    replacement = re.sub(r'([\d]+)\.([\d]+)', r'\1,\2', vttcontent)
    replacement = re.sub(r'WEBVTT.*\n\n', '', replacement)
    replacement = re.sub(r'^\d+\n', '', replacement)
    replacement = re.sub(r'\n\d+\n', '\n', replacement)

    return replacement

def vtt_to_srt(vtt_filename, srt_filename):
    with open(vtt_filename, "r") as vttfile:
        vttcontent = vttfile.read()
    
    broken_srt_content = convertcontent(vttcontent)
    fixed_srt = []
    
    # Does a quick check to see if the converted VTT has the SRT frame identifiers
    # They are not mandatory in the VTT format
    # Do a dodgy hack to add them in
    if broken_srt_content[0:2] != "1\n":
        srt_frame_counter = 1
        broken_lines = broken_srt_content.split("\n")
        for line in broken_lines:
            if "-->" in line:
                # Found a new subtitle line, first add the frame counter and increase it
                fixed_srt.append(str(srt_frame_counter) + "\n")
                srt_frame_counter += 1
            
            fixed_srt.append(line + "\n")
    else:
        srtlines = srtcontent.split("\n")
        for line in srtlines:
            fixed_srt.append(line + "\n")
    
    # Write out the file
    with open(srt_filename, "w") as srtfile:
        srtfile.writelines(fixed_srt)

def main():
    if len(sys.argv) < 2:
        print("Usage: download_9now_video OUTPUTNAME VIDEOURL [vttsubtitleurl]")
        print("Eg: download_9now_video The.Block.AU.S14E31 https://9nowvideo.com https://9nowvideo.com/videosubs.vtt")
        print("DO NOT INCLUDE THE EXTENSION IN THE OUTPUTNAME!!!")
        exit()
    
    # Setup URLs and commands
    output_filename = sys.argv[1] + ".mkv"
    video_url = sys.argv[2]
    staging_video_filename = "staged.mp4"
    staging_mkv_filename = "staged.mkv"
    staging_subs_filename = "stagedsubs.vtt"
    srt_subs_filename = "stagedsubs.srt"
    vtt_url = ""
    
    if len(sys.argv) == 4:
        use_subtitles = True
        vtt_url = sys.argv[3]
    else:
        use_subtitles = False
    
    
    download_vid_cmd = "ffmpeg -hwaccel auto -i \"{0}\" -c:a copy -c:v copy {1}".format(video_url, staging_video_filename)
    download_vtt_cmd = "wget \"{0}\" -O {1}".format(vtt_url, staging_subs_filename)
    change_container_cmd = "ffmpeg -hwaccel auto -i {0} -c:a copy -c:v copy {1}".format(staging_video_filename, staging_mkv_filename)
    
    # Begin downloading video file
    print("*** Starting Download ***")
    os.system(download_vid_cmd)
    print("*** Download Complete ***")
    
    # Dowload the subtitles if requested
    if use_subtitles:
        print("*** Starting VTT to SRT Conversion***")
        os.system(download_vtt_cmd)
        vtt_to_srt(staging_subs_filename, srt_subs_filename) # Convert the subs to SRT
        print("*** Completed VTT to SRT Conversion***")
    
    # Change container from mp4 to mkv
    print("*** Starting MP4 to MKV Conversion***")
    os.system(change_container_cmd)
    print("*** Completed MP4 to MKV Conversion***")
    
    # Merge subtitles if requested, otherwise just rename the staging mkv file
    if use_subtitles:
        print("*** Starting Muxing SRT into MKV***")
        merge_subtitle_cmd = "mkvmerge -o {0} {1} {2}".format(output_filename, staging_mkv_filename, srt_subs_filename)
        os.system(merge_subtitle_cmd)
        print("*** Completed Muxing SRT into MKV***")
    else:
        print("*** Starting Renaming staged MKV ***")
        os.rename(staging_mkv_filename, output_filename)
        print("*** Completed Renaming staged MKV ***")
    
    # Clean up the staging files
    print("*** Starting Cleaning Up Files ***")
    os.remove(staging_video_filename)
    os.remove(srt_subs_filename)
    
    if use_subtitles:
        os.remove(staging_mkv_filename)
    
    print("*** Completed Cleaning Up Files ***")

if __name__ == "__main__":
    main()