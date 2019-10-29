from rest_framework import serializers
from basic_app.models import UserProfileInfo
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileInfoSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = UserProfileInfo
        fields = ('user', 'portfolio_site')
        # fields = ('url', 'email', 'first_name', 'last_name', 'password', 'profile')

    def create(self, validated_data):
        """
        Overriding the default create method of the Model serializer.
        :param validated_data: data containing all the details of user
        :return: returns a successfully created user record
        """
        user_data = validated_data.pop('user')
        user_data['password'] = make_password(user_data['password'])
        user = UserSerializer.create(
            UserSerializer(), validated_data=user_data)
        userprofileinfo, _ = UserProfileInfo.objects.update_or_create(
            user=user, portfolio_site=validated_data.pop('portfolio_site'))
        return userprofileinfo

    def update(self, instance, validated_data):
        instance.portfolio_site = validated_data.get(
            'portfolio_site', instance.portfolio_site)
        if 'user' in validated_data:
            user = validated_data.pop('user')
            instance.user.username = user.get(
                'username', instance.user.username)
            user_password = user.get('password')
            if user_password:
                instance.user.password = make_password(user_password)
            instance.user.email = user.get(
                'email', instance.user.email)
        instance.user.save()
        instance.save()
        return instance
