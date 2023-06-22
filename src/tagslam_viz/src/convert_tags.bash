#!/bin/bash

famh=36h11
fam=36_11
srcd=`rospack find apriltag_ros`/../apriltag_image/tag${famh}
destd=`rospack find tagslam_viz`/tags/$fam
template=`rospack find tagslam_viz`/config/tag_template.dae
for i in $srcd/*.png;
do
    bname=$(basename -- "$i")
    rname=$(basename "${i%.*}")
    out=$destd/$bname
    echo converting $bname
    convert -scale 1024.0 $i $out
    cat $template | sed "s/foo\.png/$bname/g" > $destd/${rname}.dae
done

exit 0
