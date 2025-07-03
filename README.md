# ENC28J60 SPI Transaction Analyzer

![](./img/image1.png)

# Overview

The **ENC28J60** is a stand-alone Ethernet controller IC from *Microchip Technology*, designed for embedded applications. It features an integrated **10BASE-T Ethernet PHY**, a full MAC layer, and internal buffer memory. One of its key advantages is the **high-speed SPI interface**, supporting clock speeds up to **20 MHz**, allowing fast and efficient data transfer between the IC and a host microcontroller. This makes the ENC28J60 ideal for low-cost, network-connected systems such as IoT devices and embedded web servers.

The **ENC28J60 SPI Transaction Analyzer** is a high-level protocol extension for [Saleae Logic 2](https://www.saleae.com/), built to **decode and interpret SPI communication** between a microcontroller and the ENC28J60 Ethernet controller. By parsing `commands`, `register accesses`, and `data transfers`, the extension offers a clearer view of the communication process, making it easier to debug and verify Ethernet behavior at the protocol level.



# Install and Configue

<u>**Install**</u>

- Search for `ENC28J60 SPI Transaction Analyzer` in the **Extensions** tab *(you’ll find it in the right-hand sidebar)*.

- If the extension doesn't show up in the search results, it might be because your extension catalog is out of date. In that case, simply click `Check for Updates` under **More options** *(the icon with three dots)*.

- Click the `Install` button to install the extension.

- And that’s it - simple as that!

  ![](./img/image3.png)

**<u>Configue</u>**

- This extension is built on top of the **default SPI protocol analyzer**.
- First, add the built-in **SPI analyzer** to your capture.
- Then, add `"SPI ENC28J60"` as a new high-level analyzer.
- In the `"SPI ENC28J60 Settings"` window:
  - Set **Input Analyzer** to the SPI analyzer you just added.
- If everything is set correctly, decoded SPI transactions will appear with:
  - Command names
  - Register labels
  - Data bytes
  - DUMMY reads (as defined in the ENC28J60 spec)

> 💡 Tip: To improve readability, consider **disabling the default SPI analyzer** in the Data table



# Warning: Register Bank Awareness

The ENC28J60 uses four register banks to organize control registers. Many registers share the same address across banks. The active bank is selected via bits [1:0] of the ECON1 register (see Section 3.0 "Memory Organization" in the datasheet).

![](./img/image2.png)

This extension infers the current register bank using the following assumptions:

- The current bank is assumed to be Bank 0 at the start of a capture.
- The bank is also reset to Bank 0 whenever a Soft Reset (SR) command is issued.

> 🛑 If your logic capture does **not** begin at system startup or soft reset, the decoded register names may be incorrect, since bank selection might not be tracked accurately. Use caution when analyzing mid-session captures.

