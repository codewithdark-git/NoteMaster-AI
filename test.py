import g4f

def get_all_providers():
    # Retrieve all providers from the g4f library
    providers = g4f.Provider.__providers__
    provider_names = [provider.__name__ for provider in providers]
    return provider_names


all_providers = get_all_providers()
print("Available Providers:", all_providers)