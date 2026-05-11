<?php
include "waf.php";

if(!isset($_GET['p']))
    die("missing parameters");

$p = $_GET['p'];

// 邏輯：檢查第一個 ".." 之後是否還包含 "../"
// contain at most 1 of "..".
// you are not allowed to go outside root directory. If you can bypass, tell admin!!
$b = substr(strstr($p, ".."), 2);
if (strstr($b, "../"))
    die("Too many ../");

$p = "resource/".$p;

if (!file_exists($p))
    die("file not found");

header('Content-Type: image'); // 這裡是個陷阱，它強制標記為圖片
echo file_get_contents($p);
?>