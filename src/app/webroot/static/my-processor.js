// file: my-processor.js

class MyProcessor extends AudioWorkletProcessor {
  process(inputs, outputs, parameters) {
    const input = inputs[0];

    if (input.length > 0) {
      const inputChannel = input[0];
      const inputData = inputChannel.slice(); // Copy the input data

      // Send the input data back to the main thread
      this.port.postMessage(inputData);
    }

    // Returning true tells the system to keep the processor alive
    return true;
  }
}

registerProcessor("my-processor", MyProcessor);
