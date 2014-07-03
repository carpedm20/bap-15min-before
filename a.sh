while  [ : ]
do
if ps | grep "python" > /dev/null
then
    echo "Running"
else
    echo "Stopped"
    python bap15min.py
fi
done
