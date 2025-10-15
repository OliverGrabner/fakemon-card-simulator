import torch
import torch.nn as nn

# Hyperparameters 
nc = 3      # image channels (RGB)
nz = 100    # latent dimension (size of input noise)
ngf = 64    # feature maps in generator
ndf = 64    # feature maps in discriminator 

class Generator(nn.Module):
    def __init__(self, ngpu):
        super(Generator, self).__init__()
        self.ngpu = ngpu
        self.main = nn.Sequential(
            # Input is Z, going into a convolution
            # Output: (ngf*8) x 6 x 4
            nn.ConvTranspose2d(nz, ngf * 8, kernel_size=(6, 4), stride=(1, 1), padding=(0, 0), bias=False),
            nn.BatchNorm2d(ngf * 8),
            nn.ReLU(True),

            # State size: (ngf*8) x 6 x 4
            # Output: (ngf*4) x 12 x 8
            nn.ConvTranspose2d(ngf * 8, ngf * 4, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ngf * 4),
            nn.ReLU(True),

            # State size: (ngf*4) x 12 x 8
            # Output: (ngf*2) x 24 x 16
            nn.ConvTranspose2d(ngf * 4, ngf * 2, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ngf * 2),
            nn.ReLU(True),

            # State size: (ngf*2) x 24 x 16
            # Output: (ngf) x 48 x 32
            nn.ConvTranspose2d(ngf * 2, ngf, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ngf),
            nn.ReLU(True),

            # State size: (ngf) x 48 x 32
            # Output: (nc) x 96 x 64
            nn.ConvTranspose2d(ngf, nc, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.Tanh()
            # Final output size: (nc) x 96 x 64
        )

    def forward(self, input):
        return self.main(input)


class Discriminator(nn.Module):
    def __init__(self, ngpu):
        super(Discriminator, self).__init__()
        self.ngpu = ngpu
        self.main = nn.Sequential(
            # Input: (nc) x 96 x 64
            # Output: (ndf) x 48 x 32
            nn.Conv2d(nc, ndf, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.LeakyReLU(0.2, inplace=True),

            # Output: (ndf*2) x 24 x 16
            nn.Conv2d(ndf, ndf * 2, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ndf * 2),
            nn.LeakyReLU(0.2, inplace=True),

            # Output: (ndf*4) x 12 x 8
            nn.Conv2d(ndf * 2, ndf * 4, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ndf * 4),
            nn.LeakyReLU(0.2, inplace=True),

            # Output: (ndf*8) x 6 x 4
            nn.Conv2d(ndf * 4, ndf * 8, kernel_size=(4, 4), stride=(2, 2), padding=(1, 1), bias=False),
            nn.BatchNorm2d(ndf * 8),
            nn.LeakyReLU(0.2, inplace=True),

            # Final output: 1 x 1 x 1
            nn.Conv2d(ndf * 8, 1, kernel_size=(6, 4), stride=(1, 1), padding=(0, 0), bias=False),
            nn.Sigmoid()
        )

    def forward(self, input):
        return self.main(input)