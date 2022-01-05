Dim patharray(2)
Set fs = WScript.CreateObject("WScript.Shell")
Set patharray(0) =fs.CreateShortcut("c:\Users\shimo\all_workspace\python\toolcolecter\tools\myonly\irasttool\result\0.lnk")
Set patharray(1) =fs.CreateShortcut("c:\Users\shimo\all_workspace\python\toolcolecter\tools\myonly\irasttool\result\1.lnk")
patharray(0).TargetPath = "C:/Users/shimo/Desktop/ŠwZ/2021 ŒãŠú/(–Ø3)‰pŒê‰‰KD/3/(2021_09_30 14_00 Office Lens)B188G192R188.jpg"
patharray(1).TargetPath = "C:/Users/shimo/Desktop/ŠwZ/2021 ŒãŠú/(–Ø3)‰pŒê‰‰KD/4/(2021_09_30 14_00 Office Lens)B188G192R188.jpg"
patharray(0).save
patharray(1).save
