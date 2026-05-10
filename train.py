from transformers import (
    GPT2LMHeadModel, GPT2Tokenizer,
    DataCollatorForLanguageModeling,
    Trainer, TrainingArguments, TrainerCallback
)
from torch.utils.data import Dataset, random_split
import torch
import matplotlib.pyplot as plt
import numpy as np
import os


class ChordDataset(Dataset):
    def __init__(self, file_path, tokenizer, block_size=512):
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
        tokenized = tokenizer(text, return_tensors="pt", truncation=False)["input_ids"][0]
        self.examples = [tokenized[i:i+block_size] for i in range(0, len(tokenized) - block_size, block_size)]

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, i):
        return {"input_ids": self.examples[i], "labels": self.examples[i]}


class LossPlotCallback(TrainerCallback):
    def __init__(self, output_name):
        self.output_name = output_name
        self.train_losses = []   # (epoch, loss)
        self.eval_losses = []    # (epoch, loss)
        self._pending_train_loss = None

    def on_log(self, args, state, control, logs=None, **kwargs):
        if logs is None:
            return
        # Buffer the most recent train loss so we can pair it with epoch
        if "loss" in logs:
            self._pending_train_loss = (logs.get("epoch"), logs["loss"])
        if "eval_loss" in logs:
            epoch = logs.get("epoch")
            self.eval_losses.append((epoch, logs["eval_loss"]))
            # Pair with the last seen train loss at this epoch
            if self._pending_train_loss is not None:
                self.train_losses.append(self._pending_train_loss)
                self._pending_train_loss = None

    def on_train_end(self, args, state, control, **kwargs):
        self._plot()

    def _plot(self):
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        fig.suptitle(f"Training Curves — {self.output_name}", fontsize=14, fontweight="bold")

        train_epochs, train_losses = zip(*self.train_losses) if self.train_losses else ([], [])
        eval_epochs, eval_losses = zip(*self.eval_losses) if self.eval_losses else ([], [])

        # --- Left: Loss per epoch ---
        ax = axes[0]
        ax.plot(train_epochs, train_losses, color="#2563eb", linewidth=2,
                marker="o", markersize=6, label="Train loss")
        ax.plot(eval_epochs, eval_losses, color="#dc2626", linewidth=2,
                marker="s", markersize=6, label="Eval loss")
        ax.set_title("Loss per Epoch")
        ax.set_xlabel("Epoch")
        ax.set_ylabel("Loss")
        ax.set_xticks(range(1, 6))
        ax.legend()
        ax.grid(True, alpha=0.3)

        # --- Right: Perplexity per epoch ---
        ax2 = axes[1]
        if train_losses:
            train_ppl = [np.exp(l) for l in train_losses]
            ax2.plot(train_epochs, train_ppl, color="#2563eb", linewidth=2,
                     marker="o", markersize=6, label="Train perplexity")
        if eval_losses:
            eval_ppl = [np.exp(l) for l in eval_losses]
            ax2.plot(eval_epochs, eval_ppl, color="#dc2626", linewidth=2,
                     marker="s", markersize=6, label="Eval perplexity")
        ax2.set_title("Perplexity per Epoch")
        ax2.set_xlabel("Epoch")
        ax2.set_ylabel("Perplexity")
        ax2.set_xticks(range(1, 6))
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        save_path = f"./results/{self.output_name}/loss_curves.png"
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, dpi=150)
        plt.show()
        print(f"Loss curves saved → {save_path}")


def fine_tune(dataset_path, output_name):
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    special_tokens = ["<|title|>", "<|key|>", "<|chords|>"]
    tokenizer.add_special_tokens({"additional_special_tokens": special_tokens})

    model = GPT2LMHeadModel.from_pretrained("gpt2")
    model.resize_token_embeddings(len(tokenizer))

    full_dataset = ChordDataset(dataset_path, tokenizer)

    train_size = int(0.9 * len(full_dataset))
    eval_size = len(full_dataset) - train_size
    train_dataset, eval_dataset = random_split(full_dataset, [train_size, eval_size])

    collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)

    training_args = TrainingArguments(
        output_dir=f"./results/{output_name}",
        num_train_epochs=5,
        per_device_train_batch_size=8,
        gradient_accumulation_steps=4,
        eval_strategy="epoch",       # eval at end of every epoch
        save_strategy="epoch",
        save_total_limit=2,
        logging_steps=10,            # frequent step logging for buffering
        fp16=torch.cuda.is_available(),
        load_best_model_at_end=True,
    )

    loss_callback = LossPlotCallback(output_name)

    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=collator,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        callbacks=[loss_callback],
    )

    trainer.train()
    model.push_to_hub(f"CS429/{output_name}")
    tokenizer.push_to_hub(f"CS429/{output_name}")
    print(f"Done — {output_name} pushed to Hugging Face")


fine_tune("train_harte.txt", "gpt2-harte")