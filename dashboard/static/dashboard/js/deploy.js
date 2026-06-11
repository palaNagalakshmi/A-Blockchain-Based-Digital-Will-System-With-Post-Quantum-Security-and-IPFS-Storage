document.addEventListener("DOMContentLoaded", function () {

    const deployBtn = document.getElementById("deployContractBtn");

    // If button not on page → do nothing
    if (!deployBtn) return;

    deployBtn.addEventListener("click", async function () {

        const status = document.getElementById("deployStatus");

        if (!window.ethereum) {
            alert("MetaMask not installed");
            return;
        }

        try {
            status.innerText = "🔌 Connecting wallet...";

            const accounts = await window.ethereum.request({
                method: "eth_requestAccounts"
            });

            const account = accounts[0];

            // Optional: Check network (Polygon Amoy chainId = 80002)
            const chainId = await window.ethereum.request({
                method: "eth_chainId"
            });

            if (chainId !== "0x13882") { // 80002 in hex
                alert("Please switch to Polygon Amoy network");
                status.innerText = "❌ Wrong network";
                return;
            }

            status.innerText = "📦 Loading contract...";

            const response = await fetch("/static/abi/DigitalWill.json");
            const contractJson = await response.json();

            const web3 = new Web3(window.ethereum);

            const contract = new web3.eth.Contract(contractJson.abi);

            status.innerText = "🚀 Deploying contract... Please confirm in MetaMask";

            const deployedContract = await contract.deploy({
                data: contractJson.bytecode
            }).send({
                from: account,
                gas: 3000000
            });

            const contractAddress = deployedContract.options.address;

            status.innerHTML = `<span class="status-success">✅ Deployed at: ${contractAddress}</span>`;

            // Save address to Django
            await fetch("/save-contract-address/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify({
                    contract_address: contractAddress
                })
            });

            alert("✅ Contract deployed successfully!");

        } catch (error) {
            console.error("Deployment Error:", error);
            status.innerHTML = `<span class="status-error">❌ Deployment failed</span>`;
        }
    });

});


function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(
                    cookie.substring(name.length + 1)
                );
                break;
            }
        }
    }

    return cookieValue;
}